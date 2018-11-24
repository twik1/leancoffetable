import pymysql
import time
import datetime
import sys
import json

class DBMySQL:
    def __init__(self, ip, usr, pwd, db):
        """ Init for the MySQL class

        :param ip:
            IP address to the MySQL server
        :param usr:
            Username for the lctdb database
        :param pwd:
            Password for the lctdb database
        :param db:
            Name of the lctdb database
        """
        self.ip = ip
        self.usr = usr
        self.pwd = pwd
        self.datbase = db

    def set_param(self, ip, usr, pwd, db):
        self.ip = ip
        self.usr = usr
        self.pwd = pwd
        self.datbase = db

    def conn(self):
        """ Connect to the MySQL database

        :return:
            0 If success
            1 If unable to connect
            2 Faulty user of password

            4 Unknown error
        """
        try:
            self.db = pymysql.connect(self.ip,self.usr,self.pwd,self.datbase)
            self.cursor = self.db.cursor()
            return 0
        except pymysql.err.OperationalError as err:
            if err.args[0] == '2003':
                return 1 # Unable to connect
            if err.args[0] == '1045':
                return 2 # Fault user ow password
            return 4 # Unknown error

    def disconn(self):
        """ Disconnect from the MySQL database

        :return:
            Nothing
        """
        self.db.close()


    def db_set(self, sql):
        """ Execute a SQL statement towards the database

        :param sql:
            A string with a SQL statement
            not expecting any thing in return
        :return:
            Nothing
        """
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Commit your changes in the database
            self.db.commit()
        except:
            # Rollback in case there is any error
            print("Exception error: {0}".format(sys.exc_info()[0]))
            self.db.rollback()


    def db_get(self, sql):
        """ Execute a SQL statement towards the database

        :param sql:
            A string with a SQL statement
            expecting some kind of result
        :return:
            Returning a tuple
        """
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except:
            # Rollback in case there is any error
            print("Exception error: {0}".format(sys.exc_info()[0]))


    # Document further and maybe change name to db_test
    def test_connection(self):
        """ Test the database connection

        :return:
        """
        res = self.conn()
        if not res == 0:
            return res
        sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = \'{}\' ".format(self.datbase)
        restup = self.db_get(sql)
        self.disconn()
        if restup is None:
            return 3 # No database
        return res


##############################################################


#    def get_users(self):
#        userlist = []
#        sql = "SELECT * FROM user"
#        usertup = self.db_get(sql)
#        for user in usertup:
#            userlist.append({'user': user[0]})
#        return userlist


    def get_user(self, user):
        """ Get a user from the lctdb

        :param user:
            Username string
        :return:
            A list with a dictionary of the user data
            [{user:twik, name:Tommy, password:supersecret, mail:twik@duckdns.org}]
            Empty if user doesn't exist ?

        """
        uservalues = []
        usertup = ()
        sql = "SELECT * FROM user WHERE user = '%s'" % user
        usertup = self.db_get(sql)
        if len(usertup):
            usertup = usertup[0]
            uservalues.append({'user': usertup[0], 'name': usertup[1], 'password': usertup[2],'mail': usertup[3]})
        return uservalues


    def check_user(self, user):
        """ Check if a user exists in the lctdb

        :param user:
            Username string
        :return:
            True if user exists
            False if user doesn't exists
        """
        if self.get_user(user):
            return True
        else:
            return False


    def add_user(self, obj):
        """ Add a user to the lctdb

        :param obj:
            A dictionary with a set of key:values
            Mandatory:
                user, password, mail
            Optional:
                name
        :return:
            Nothing
        """
        sql = \
              "INSERT INTO user(user,name,password,mail,created,updated) \
VALUES ('%s','%s','%s','%s',null,null) ON DUPLICATE KEY UPDATE \
name='%s',password='%s',mail='%s',created=null,updated=null" % \
(obj['user'],obj['name'],obj['password'],obj['mail'],obj['name'],obj['password'],obj['mail'])
        self.db_set(sql)


    def del_user(self, user):
        """ Delete a user from the lctdb

        :param user:
            Username string
        :return:
            Nothing
        """
        sql = "DELETE FROM user WHERE user='%s'" % user
        self.db_set(sql)


###############################################################


    def get_boards(self):
        """ Get all boards from the lctdb

        :return:
            A list of dictionaries of [{boardid:<boardid>},{boardid:<boardid>}]
            Empty if no board is found
        """
        boardlist = []
        boardtup = ()
        sql = "SELECT * FROM board"
        boardtup = self.db_get(sql)
        for board in boardtup:
            boardlist.append({'boardid': board[0]})
        return boardlist


    def add_board(self, obj):
        """ Add a board to the lctdb

        :param obj:
            A dictionary with a set of key:values
            Mandatory:
                username, boardname, startdate, votenum
                Rename to user to be consistent?

        :return:
            Nothing
        """
        sql = \
              "INSERT INTO board(user,name,startdate,votenum,created,updated) \
VALUES ('%s','%s','%s','%s',null,null) ON DUPLICATE KEY UPDATE \
user='%s',name='%s',startdate='%s',votenum='%s',created=null,updated=null" % \
(obj['username'], obj['boardname'], obj['startdate'],obj['votenum'],obj['username'], \
 obj['boardname'],obj['startdate'],obj['votenum'])
        print(sql)
        self.db_set(sql)

    def update_board(self, obj):
        """ Update a board in the lctdb

        :param obj:
            A dictionary with a set of key:values
            Mandatory:
                username, boardname, startdate, votenum
                Rename to user to be consistent?
        :return:
            Nothing
        """
        sql = \
            "INSERT INTO board(boardid,user,name,startdate,votenum,created,updated) \
VALUES ('%s','%s','%s','%s','%s',null,null) ON DUPLICATE KEY UPDATE \
user='%s',name='%s',startdate='%s',votenum='%s',created=null,updated=null" % \
(obj['boardid'],obj['username'], obj['boardname'], obj['startdate'],obj['votenum'], \
 obj['username'], obj['boardname'],obj['startdate'],obj['votenum'])
        self.db_set(sql)


    def get_board(self, boardid):
        """ Get a board from lctdb

        :param boardid:
            Id of the board
        :return:
            A list with a dictionary of the board data
            [{boardid:1, name:Test board, user:twik, date:xxxx, votenum: 3}]
            Empty if board doesn't exist ?
        """
        boardvalues = []
        sql = "SELECT * FROM board WHERE boardid = '%s'" % boardid
        boardtup = self.db_get(sql)
        if len(boardtup):
            boardtup = boardtup[0]
            boardvalues.append({'boardid': boardtup[0], 'name': boardtup[1], 'user': boardtup[2], 'date':boardtup[3],'votenum':boardtup[4]})
        return boardvalues


    def check_board(self, boardid):
        """ Check to see if a boardid exists

        :param boardid:
            Id of the board
        :return:
            True if board exist
            False if board doesn't exist
        """
        if self.get_board(boardid):
            return True
        else:
            return False


    def del_board(self, boardid):
        """ Delete a boardid

        :param boardid:
            The id of the board to be deleted
        :return:
            Nothing?
        """
        sql = "DELETE FROM board WHERE boardid = '%s'" % boardid
        self.db_set(sql)


################################################################


    def get_topics(self, boardid):
        """ Get all topics for a certain boardid

        :param boardid:
            Id of the board to search for topics
        :return:
            A list of dictionaries of [{topicid:<topicid1>},{topicid:<topicid2>}]
            Empty if no topic is found
        """
        topiclist = []
        sql = "SELECT * FROM topic WHERE boardid = '%s'" % boardid
        topictup = self.db_get(sql)
        for topic in topictup:
            topiclist.append({'topicid': topic[0]})
        return topiclist


    def add_topic(self, obj):
        """ Add a topic to the boardid in the lctdb

        :param obj:
            A dictionary with a set of key:values
            Mandatory:
                boardid, heading, description, username
                Rename to user to be consistent?            A dictionary with a set of key:values
            Mandatory:
                boardid, heading, description, username
                Rename to user to be consistent?
        :return:
            Nothing
        """
        sql = \
            "INSERT INTO topic(boardid,heading,description,user,created,updated) \
VALUES ('%s','%s','%s','%s',null,null) ON DUPLICATE KEY UPDATE \
boardid='%s',heading='%s',description='%s',user='%s',created=null,updated=null" % \
            (obj['boardid'], obj['heading'], obj['description'], obj['username'], \
             obj['boardid'], obj['heading'], obj['description'], obj['username'])
        self.db_set(sql)


    def update_topic(self, obj):
        """ Update a topic for a boardid in the lctdb

        :param obj:
            A dictionary with a set of key:values
            Mandatory:
                boardid, heading, description, username
                Rename to user to be consistent?
                Is this function used? it needs topicid?
        :return:
            Nothing
        """
        sql = \
            "INSERT INTO topic(boardid,heading,description,user,created,updated) \
VALUES ('%s','%s','%s','%s',null,null) ON DUPLICATE KEY UPDATE \
boardid='%s',heading='%s',description='%s',user='%s',created=null,updated=null" % \
            (obj['boardid'], obj['heading'], obj['description'], obj['username'], \
             obj['boardid'], obj['heading'], obj['description'], obj['username'])
        self.db_set(sql)


    def get_topic(self, topicid):
        """ Get a topic from lctdb

        :param topicid:
            Id of the topic
        :return:
            A list with a dictionary of the topic data
            [{topicid:1, boardid:1, heading:Topic head, description:Topic desc, user:twik}]
            Empty if board doesn't exist ?
        """
        topicvalues = []
        sql = "SELECT * FROM topic WHERE topicid = '%s'" % topicid
        topictup = self.db_get(sql)
        if len(topictup):
            topictup = topictup[0]
            topicvalues.append({'topicid':topictup[0],'boardid':topictup[1],'heading': topictup[2],
                                'description': topictup[3], 'user':topictup[4]})
        return topicvalues


    def check_topic(self, topicid):
        """ Check to see if a topicid exists

        :param topicid:
            Id of the topic
        :return:
            True if topicid exist
            False if topicid doesn't exist
        """
        if self.get_topic(topicid):
            return True
        else:
            return False


    def del_topic(self, topicid):
        """ Delete a topicid

        :param topicid:
            Id of the topic to be deleted
        :return:
            Nothing
        """
        sql = "DELETE FROM topic WHERE topicid = '%s'" % topicid
        self.db_set(sql)


###################################################################


    def get_votes(self,boardid,topicid):
        """ Get votes for a topicid

        :param boardid:
            boardid, maybe not used?
        :param topicid:
            The topicid to search for votes
        :return:
            A list of dictionaries of [{voteid:<voteid1>},{voteid:<voteid2>}]
            Empty if no voteid is found
        """
        votelist = []
        sql = "SELECT * FROM votes WHERE topicid = '%s'" % topicid
        votetup = self.db_get(sql)
        for vote in votetup:
            votelist.append({'voteid': vote[0]})
        return votelist


    def add_vote(self, obj):
        """ Add a vote to a topicid

        :param obj:
            A dictionary with a set of key:values
            Mandatory:
                topicid, user,
        :return:
            Nothing
        """
        sql = \
            "INSERT INTO votes(user,topicid) \
VALUES ('%s','%s') ON DUPLICATE KEY UPDATE user='%s',topicid='%s'" % \
        (obj['user'], obj['topicid'],obj['user'], obj['topicid'])
        self.db_set(sql)


    def get_vote(self, topicid, voteid):
        """ Get a voteid

        :param topicid:
            topicid, maybe not used?
        :param voteid:
            Id of the vote
        :return:
            A list with a dictionary of the topic data
            [{user:twik, topicid:1}]
            Empty if voteid doesn't exist ?
        """
        votevalues = []
        sql = "SELECT * FROM votes WHERE voteid = '%s'" % voteid
        votetup = self.db_get(sql)
        if len(votetup):
            votetup = votetup[0]
            votevalues.append({'user': votetup[1],'topicid': votetup[2]})
        return votevalues


    def check_vote(self, voteid):
        """ Check to see if a voteid exists

        :param voteid:
            Id of the vote
        :return:
            True if voteid exist
            False if voteid doesn't exist
        """
        if self.get_vote(voteid):
            return True
        else:
            return False


    def del_vote(self, voteid):
        """ Delete a voteid

        :param voteid:
            Id of the vote to be deleted
        :return:
            Nothing
        """
        sql = "DELETE FROM votes WHERE voteid = '%s'" % voteid
        self.db_set(sql)
