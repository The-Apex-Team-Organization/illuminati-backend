from django.db import connection, transaction, OperationalError
from .models import VoteTypes
from datetime import datetime, timedelta, date
from enums.rules import VoteRules, PromoteRules
from enums.roles import Role


class VoteService:

    def __init__(self, user):
        self.user = user


    @staticmethod
    def get_vote_role_raw(user_role):

        vote_types = list(
            VoteTypes.objects
            .filter(user_role = user_role)
            .values_list('vote_type', flat = True)
        )

        return vote_types


    def get_all_votes(self):

        vote_types = self.get_vote_role_raw(self.user.role)

        if not vote_types:
            return []

        placeholders = ','.join(['%s'] * len(vote_types))

        query = f"""
                SELECT v.id, v.name, v.vote_type
                FROM votes v
                LEFT JOIN vote_users vu
                ON v.id = vu.vote_id
                AND vu.user_id = %s
                WHERE (vu.id IS NULL OR vu.is_voted = FALSE)
                AND v.is_active = TRUE
                AND v.vote_type IN ({placeholders});
            """

        params = [self.user.id] + vote_types

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            params.clear()


        votes = []

        for vote in rows:

            user_roles = set()
            for role in PromoteRules.new_rules.get(vote[2]):
                user_roles.add(role)

            placeholders = ','.join(['%s'] * len(user_roles))

            query_total_count = f"""
                                SELECT COUNT(u.id)
                                FROM users u
                                WHERE u.role in ({placeholders});
                                """


            with connection.cursor() as cursor:
                cursor.execute(query_total_count, list(user_roles))
                count_of_all_users = cursor.fetchall()

            query_already_voted = f"""
                        SELECT COUNT(*)
                        FROM users u
                        JOIN vote_users vu
                        ON u.id = vu.user_id
                        WHERE u.role in ({placeholders})
                        AND vu.vote_id = %s;
            """

            params = list(user_roles) + [vote[0]]


            with connection.cursor() as cursor:
                cursor.execute(query_already_voted, params)
                count_of_voting_users = cursor.fetchall()

            votes.append({
                'id': vote[0],
                'name': vote[1],
                'percent' : int((count_of_voting_users[0][0] / count_of_all_users[0][0]) * 100)
            })

        return votes


    @staticmethod
    def close_votes(date):

        query_to_change = """   
                    SELECT v.amount_of_agreed, v.amount_of_disagreed, v.user_in_question_id, v.vote_type
                    FROM votes v
                    WHERE v.date_of_end < %s AND v.is_active = TRUE;
                    """

        query_to_update = """
                        UPDATE votes v
                        SET v.is_active = False
                        WHERE v.date_of_end < %s;
                        """

        params = [date]

        with connection.cursor() as cursor:
            cursor.execute(query_to_change, params)
            rows = cursor.fetchall()
            cursor.execute(query_to_update, params)

        list_of_users_to_promote = [
            {
                'count_of_agreed': v[0],
                'count_of_disagreed': v[1],
                'user_id' : v[2],
                'vote_type' : v[3]
            }
            for v in rows
            if v[3] in list(PromoteRules.rules.keys())

        ]

        list_of_users_to_ban = [
            {
                'count_of_agreed': v[0],
                'count_of_disagreed': v[1],
                'user_id': v[2]
            }
            for v in rows
            if v[3] == 'BAN_USER'
        ]

        UserPromoteService.promote_user(list_of_users_to_promote)
        UserBanService.ban_user(list_of_users_to_ban)

        return True



class SendVoteService:

    def user_already_voted(self, user_id, vote_id):
        query = """
                    SELECT is_voted 
                    FROM vote_users 
                    WHERE user_id = %s 
                    AND vote_id = %s
                """

        params = [user_id, vote_id]
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        if rows is None or len(rows) == 0:
            return False

        else:
            return True


    def commit_choice(self, user_id, vote_id, choice):

        if choice == "AGREE":
            query = """
            
                    START TRANSACTION;
    
                    INSERT INTO vote_users(user_id, vote_id, is_voted) 
                    VALUES (%s, %s, TRUE);
                                            
                    UPDATE votes v
                    SET v.amount_of_agreed = v.amount_of_agreed + 1
                    WHERE v.id = %s;
                    
                    COMMIT;
                    """

            params = [user_id, vote_id, vote_id]

            with connection.cursor() as cursor:
                cursor.execute(query, params)

            return True


        elif choice == "DISAGREE":
            query = """
                    START TRANSACTION;
        
                    INSERT INTO vote_users(user_id, vote_id, is_voted)
                    VALUES (%s, %s, TRUE);
        
                    UPDATE votes v
                    SET v.amount_of_disagreed = v.amount_of_disagreed + 1
                    WHERE v.id = %s;
        
                    COMMIT;
                    """

            params = [user_id, vote_id, vote_id]

            with connection.cursor() as cursor:
                cursor.execute(query, params)

            return True

        return False



class PermissionService:

    def __init__(self, user):
        self.user = user


    def architect_exists(self):
        query = """
                SELECT 1
                WHERE EXISTS (
                    SELECT * 
                    FROM users u 
                    WHERE u.role = %s
                );
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [Role.ARCHITECT.value])
            rows = cursor.fetchall()


        if len(rows) == 1:
            return True

        return False



    def has_promote_permission(self):

        if (self.user.role == Role.ARCHITECT.value or
                (self.user.role == Role.GOLD_MASON.value and self.architect_exists())):
            return False


        query = """
                SELECT up.date_of_last_promotion, up.is_promote_requested
                FROM users_promotions up
                WHERE up.user_id = %s;
                """

        params = [self.user.id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        votes_dicts = [{'date': v[0], 'send_request': v[1]} for v in rows]

        last_promo_date  = votes_dicts[0]['date']

        today = last_promo_date .today()
        count_days = (today - last_promo_date ).days

        if count_days > 0 and votes_dicts[0]['send_request'] == False:
            return True

        return False


    def has_ban_permission(self):
        query = """
            SELECT u.is_inquisitor
            FROM users u 
            WHERE u.id = %s;
        """
        params = [self.user.id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        is_inquisitor = rows[0][0]

        if is_inquisitor:
            return True

        return False


    def get_all_users_for_ban(self):

        query = """
            SELECT u.id, u.username
            FROM users u
            WHERE u.id NOT IN (
                SELECT user_in_question_id
                FROM (
                    SELECT v.user_in_question_id
                    FROM votes v
                    WHERE v.is_active = TRUE
                    AND v.vote_type = 'BAN_USER'
                ) AS tmp
            );
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        list_of_users_for_ban = [
            {
                "user_id" : u[0],
                "username" : u[1]
            }
            for u in rows

        ]

        return list_of_users_for_ban



class UserPromoteService:

    def __init__(self, user):
        self.user = user


    def create_vote(self):
        query = """
                START TRANSACTION;
                    
                UPDATE users_promotions up
                SET up.is_promote_requested = TRUE
                WHERE up.user_id = %s;    
                    
                INSERT INTO votes(name, is_active, user_in_question_id, vote_type, date_of_end)
                VALUES (%s, %s, %s, %s, %s);
                    
                COMMIT;
                """

        next_role = VoteRules.rules.get(self.user.role)
        vote = f"Promote user {self.user.username} to {PromoteRules.rules.get(next_role).value}"
        date_of_end = datetime.now() + timedelta(hours = 24)

        params = [self.user.id, vote, True, self.user.id, VoteRules.rules.get(self.user.role), date_of_end]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return True


    @staticmethod
    def promote_user(values):

        for value in values:
            count_of_agreed = value.get('count_of_agreed')
            count_of_disagreed = value.get('count_of_disagreed')

            if (count_of_agreed / (count_of_disagreed + count_of_agreed)) > 0.5:
                query = """
                    START TRANSACTION;
                        
                    UPDATE users u
                    SET u.role = %s 
                    WHERE u.id = %s;
                        
                    UPDATE users_promotions up
                    SET up.date_of_last_promotion = %s, 
                    up.is_promote_requested = False
                    WHERE up.user_id = %s;
                        
                    COMMIT;
                    """

                date_of_end = datetime.now() + timedelta(days = 42)

                new_user_role = PromoteRules.rules.get(value.get('vote_type')).value
                params = [new_user_role, value.get('user_id'), date_of_end, value.get('user_id')]

                with connection.cursor() as cursor:
                    cursor.execute(query, params)

        return True




class UserBanService:

    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username


    def create_vote(self):
        query = """
                INSERT INTO votes(name, is_active, user_in_question_id, vote_type, date_of_end)
                VALUES (%s, %s, %s, %s, %s);
                """

        vote = f"Ban user {self.username}"
        date_of_end = datetime.now() + timedelta(hours = 4)

        params = [vote, True, self.user_id, 'BAN_USER', date_of_end]

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return True


    @staticmethod
    def ban_user(values):

        for value in values:
            count_of_agreed = value.get('count_of_agreed')
            count_of_disagreed = value.get('count_of_disagreed')

            if (count_of_agreed / (count_of_disagreed + count_of_agreed)) > 0.5:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO prohibited_ip(ip_address)
                            SELECT ip_address
                            FROM users_ip
                            WHERE user_id = %s;
                            """,
                            [value.get('user_id')]
                        )

                        cursor.execute(
                            "DELETE FROM users WHERE id=%s;",
                            [value.get('user_id')]
                        )

        return True



class InquisitorManagementService:

    def appoint_inquisitor_role(self):
        query = """
            UPDATE users u
            SET u.is_inquisitor = TRUE
            WHERE u.id = (
                SELECT id
                FROM (
                    SELECT id
                    FROM users
                    ORDER BY RAND()
                    LIMIT 1
                ) AS t
            );
        """

        try:

            with connection.cursor() as cursor:
                cursor.execute(query)

            return True

        except OperationalError as e:
            raise RuntimeError(f"Database problem connection or table lock: {e.args[0]}")


    def remove_inquisitor_role(self):

        query = """
            UPDATE users u
            SET u.is_inquisitor = FALSE
            WHERE u.is_inquisitor = TRUE
        """

        try:

            with connection.cursor() as cursor:
                cursor.execute(query)

            return True

        except OperationalError as e:
            raise RuntimeError(f"Database problem connection or table lock: {e.args[0]}")



class UserArchitectService:

    def add_to_hall_of_fame(self, user_id, username, email):
        query = """
                INSERT INTO hall_of_fame(username, email)
                VALUES (%s, %s);
                    
                DELETE FROM users WHERE id = %s;
        """

        params = [username, email, user_id]

        with connection.cursor() as cursor:
            cursor.execute(query, params)


    def delete_architect(self):
        query = """
            SELECT u.id, u.username, u.email, up.date_of_last_promotion
            FROM users_promotions up
            JOIN users u ON up.user_id = u.id
            WHERE u.role = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [Role.ARCHITECT.value])
            rows = cursor.fetchall()


        if len(rows) > 0:
            user_id = rows[0][0]
            username = rows[0][1]
            email = rows[0][2]
            expired_date = rows[0][3] + timedelta(days = 42)

            if expired_date < datetime.now().date():
                self.add_to_hall_of_fame(user_id, username, email)
                return True

            return False

        return False
