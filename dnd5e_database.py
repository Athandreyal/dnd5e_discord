import sqlite3

debug = lambda *args, **kwargs: False  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug
# intend this file for database specific interactions.
# Creating tables, reading from them, saving/loading characters, etc.

database = sqlite3.connect('players.db')
sql_c = database.cursor()


def database_init():
    sql_c.execute('create table if not exists players (' +
                  'id text, ' +
                  'name text, ' +
                  'age integer, ' +
                  'height integer, ' +
                  'weight integer, ' +
                  'level integer, ' +
                  'experience integer, ' +
                  'unspent_pts integer, ' +
                  'race text, ' +
                  'class text, ' +
                  'background text, ' +
                  'path text, ' +
                  'skills text, ' +
                  'str integer, ' +
                  'con integer, ' +
                  'dex integer, ' +
                  'int integer, ' +
                  'wis integer, ' +
                  'cha integer, ' +
                  'hp_dice integer, ' +
                  'hp_current integer, ' +
                  'party_id integer, ' +
                  'status text, ' +
                  'equipment text, ' +
                  'primary key (id, name)' +
                  ');')
    sql_c.execute('create unique index if not exists idx_characters on players(id, name);')
    sql_c.execute('create table if not exists equipment (' +
                  'id text, ' +
                  'name text, ' +
                  'left_hand text, ' +
                  'right_hand text, ' +
                  'armor text, ' +
                  'shield text, ' +
                  'back text, ' +
                  'jaw text, ' +
                  'collar text, ' +
                  'neck text, ' +
                  'gloves text, ' +
                  'fingers text, ' +
                  'belt text, ' +
                  'shoulders text, ' +
                  'inventory text, ' +
                  'foreign key (id, name) references players (id, name)'
                  ');')
    sql_c.execute('create table if not exists parties (' +
                  'party_id integer, ' +
                  'player_id text, ' +
                  'player_name text, ' +
                  'leader text, ' +
                  'primary key (party_id, player_id, player_name)' +
                  ');')
    sql_c.execute('create unique index if not exists idx_party on parties(party_id, player_id, player_name);')
    sql_c.execute('pragma synchronous = 1')
    sql_c.execute('pragma journal_mode = wal')
    sql_c.execute('pragma foreign_keys = 1')
    database.commit()
    # weapons, armor, and items, or just items.....
    #   ^ relation to attribute the two from separate tables?


def set_party(id, player_id, player_name, leader=False):
    sql_c.execute('insert or replace into parties(party_id, player_id, player_name, leader) ' +
                  'values(%d, "%s", "%s", "%s");' % (id, player_id, player_name, leader))
    database.commit()

    # makes the table, and inserts players.
    # create table if not exists parties ( party_id integer, player_id text, player_name text, leader text, primary key (party_id, player_id, player_name), foreign key (player_id, player_name) references players(id, name));


def leave_party(id, player_id, player_name):
    sql_c.execute('delete from parties where party_id=? and player_id=? and player_name=?;',
                  (id, player_id, player_name,))
    # escalate another member to leader
    party_members = sql_c.execute('select player_id, player_name from parties where party_id=?;', (id,)).fetchall()
    if party_members:
        p_id, p_name = party_members[0]
        sql_c.execute('update parties set leader="True" where party_id=? and player_id=? and player_name=?;',
                      (id, p_id, p_name,))
    database.commit()


def get_parties(player_id):
    return sql_c.execute('select * from parties where player_id=?',
                         (player_id,)).fetchall()


def get_party_member(player_id, player_name):
    return sql_c.execute('select * from parties where player_id=? and player_name=?',
                         (player_id, player_name,)).fetchone()


def create_party(player_id, player_name):
    # todo: improve this to get an unused slot, rather than always just the next largest
    party_max = sql_c.execute('select max(party_id) from parties').fetchone()[0]
    if party_max == "NULL" or party_max is None:
        party_max = 0
    else:
        party_max = int(party_max)
    sql_c.execute('insert or replace into parties(party_id, player_id, player_name, leader) ' +
                  'values (%d, "%s", "%s", "True");' % (party_max, player_id, player_name))
    database.commit()


def parties():
    return sql_c.execute('select * from parties').fetchall()


def get_player_party_leaders(player_id):
    return sql_c.execute('select * from players join (select player_id, player_name from parties where player_id=? ' +
                         'and  leader="True")leaders on leaders.player_id=players.id and ' +
                         'leaders.player_name=players.name;', (player_id,)).fetchall()


def get_players_in_party(party_id):
    return sql_c.execute('select * from players join (select player_id, player_name from parties where party_id=? ' +
                         ')leaders on leaders.player_id=players.id and ' +
                         'leaders.player_name=players.name;', (party_id,)).fetchall()


def get_players(u):
    return sql_c.execute('select * from players where id = ?', (u,)).fetchall()


def get_player(u, n):
    return sql_c.execute('select * from players where id = ? and name = ?', (u, n)).fetchall()


def set_player(p):
    sql_c.execute('insert or replace into players (id, name, age, height, weight, level, experience, unspent_pts, ' +
                  'race, class, background, path, skills, str, con, dex, int, wis, cha, hp_dice, hp_current, ' +
                  'equipment) values (:uid, :name, :age, :height, :weight, :level, :experience, :unspent_pts, :race, ' +
                  ':class, :background, :path, :skills, :str, :con, :dex, :int, :wis, :cha, :hp_dice, :hp_current, ' +
                  ':equipment);', p)
    database.commit()


def database_char_tuple_to_dict(c):
    return {
            'uid': c[0],
            'name': c[1],
            'age': c[2],
            'height': c[3],
            'weight': c[4],
            'level': c[5],
            'experience': c[6],
            'unspent_pts': c[7],
            'race': c[8],
            'class': c[9],
            'background': c[10],
            'path': c[11],
            'skills': c[12],
            'str': c[13],
            'con': c[14],
            'dex': c[15],
            'int': c[16],
            'wis': c[17],
            'cha': c[18],
            'hp_dice': c[19],
            'hp_current': c[20],
            'equipment': c[21]
            }
