import discord
import asyncio
import MySQLdb
import datetime
import json
import yaml
import sys
import os
import errno

from discord.ext import commands

start_nest = datetime.date(2018,8,22)
td = datetime.timedelta(days=14)


bot = commands.Bot(command_prefix="$")
bot.remove_command("help")

configFilename="NestBotConfig.yml"

with open(configFilename, 'r') as yamlConfig:
    cfg = yaml.load(yamlConfig)


mysql_host=cfg['database']['mysql-host'] 
mysql_user=cfg['database']['mysql-user'] 
mysql_pass=cfg['database']['mysql-pass'] 
mysql_db=cfg['database']['mysql-db']     
mysql_table=cfg['database']['mysql-tbl']

park_list = []
for i in cfg['parks']:
    park_list.append(i)

admins = []
for i in cfg['admin']:
    admins.append(i)

def get_current_date():
    return datetime.datetime.now().strftime ("%Y%m%d")

def look_for_nest_period(d):
    start = ""
    original_nest_start = datetime.date(2018,8,22)
    begin_nest = original_nest_start
    td = datetime.timedelta(days=14)
    end_nest = original_nest_start + td
    found = False
    while found == False:
        if d >= begin_nest and d <= end_nest:
            found = True
            return(begin_nest,end_nest)
        else:
            # find the next begin/end
            begin_nest = end_nest
            end_nest = begin_nest + td
            
def execute_sql_command(sql_command):
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    print("Executing: %s" % sql_command)
    print(cur.execute(sql_command))
    db.commit()
    db.close()

def get_sql_response(sql_command):
    resp = []
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    cur.execute(str_command)
    while True:
        row = cur.fetchone()
        print(row)
        if row == None:
            break
        resp.append(row)
    db.close()
    return resp

def check_for_table(table):
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    str_command = "SHOW TABLES LIKE \'" + table + "\'"
    cur.execute(str_command)    
    row = cur.fetchone()
    db.close()
    if row is not None:
        print("Table exists")
        return True
    else:
        print("Table not found...")
        return False
        #str_command = "CREATE TABLE " + table + " (parkName VARCHAR(64), nestMon VARCHAR(64), lat DOUBLE NOT NULL, lon DOUBLE NOT NULL);"
        #execute_sql_command(str_command)
        
def check_park(park):
    if park in park_list:
        return True
    else:
        return False

def verify_admin(user):
    if user in admins:
        return True
    else:
        return False

@bot.event
async def on_ready():
    print("Bot {} has successfully logged in. Servicing {} guilds".format(bot.user.name, len(bot.guilds)))
    await bot.change_presence(activity=discord.Game("With itsself..."))

@bot.check_once
def whitelist(ctx):
    return ctx.message.author.id in admins

@bot.command(pass_context=True)
async def setnest(ctx, *args):
    park_name = args[0]
    nest_mon = args[1]
    if verify_admin(ctx.message.author.id):
        print("We can run this command!")

@bot.command(pass_context=True)
async def settable(ctx, *args):
    table_name = args[0]
    if check_for_table(table_name) == False:
    	str_command = "CREATE TABLE " + table_name + " (parkName VARCHAR(64), nestMon VARCHAR(64), lat DOUBLE NOT NULL, lon DOUBLE NOT NULL);"
    	execute_sql_command(str_command)


'''
@bot.command(pass_context=True)
async def getgym(ctx, *args):
    channel = str(ctx.message.channel.name)
    str_command = "SELECT * from " + mysql_table + " WHERE gymname=\'" + args[0] + "\';";
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    cur.execute(str_command)
    row = cur.fetchone()
    if row != None:
        name = row[0]
        city = row[1]
        lat = row[2]
        lng = row[3]
        latlng = '{:5f},{:5f}'.format(lat, lng)
        link = 'http://maps.google.com/maps?q={}'.format(latlng)
        #print(row)
        await ctx.channel.send(link)
    else:
        await ctx.channel.send("I'm sorry that gym as not found, try: $getgymlist for a list of Gyms.")
    db.close()

@bot.command(pass_context=True)
async def getgymlist(ctx, *args):
    str_command = "SELECT * from " + mysql_table + " WHERE city=\'" + args[0] + "\';";
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    gyms_list = []
    if args[0] in city_list:
        cur.execute(str_command)
        while True: 
            row = cur.fetchone()
            print(row)
            if row == None:
                break
            gyms_list.append(row)
        str_reply = "```"
        for i in gyms_list:
            #for j in i:
            str_reply = str_reply + str(i[0]) + "\n"
            #str_reply = str_reply + "\n"
        str_reply = str_reply + '\n```'
        await ctx.channel.send(str_reply)
    db.close()

@bot.command(pass_context=True)
async def getallgyms(ctx, *args):
    if check_city(args[0]):
        str_command = "SELECT * from " + mysql_table + " WHERE city=\'" + args[0] + "\';";
    else:
        await ctx.channel.send("The city does not exist in the database\nexample: $getallgyms Sykesville")
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    gyms_list = []
    cur.execute(str_command)
    while True:
        row = cur.fetchone()
        print(row)
        if row == None:
            break
        gyms_list.append(row)
    db.close()
    print(gyms_list)
    str_reply = ""
    for i in gyms_list:
        lat = i[2]
        lng = i[3]
        latlng = '{:5f},{:5f}'.format(lat, lng)
        link = 'http://maps.google.com/maps?q={}'.format(latlng)
        str_reply += '{} - {}\n'.format(i[0],link)
    await ctx.channel.send(str_reply)


@bot.command(pass_context=True)
async def addgym(ctx, *args):
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    if ctx.message.author.id in admins:
        channel = str(ctx.message.channel.name)
        print(args)
        process = True
        if len(args[0]) > 64:
            await ctx.channel.send("ugh what did you put in? That Name is way too long.")
            process = False         
        if len(args[1]) > 64:
            await ctx.channel.send("ugh what did you put in? That City is way too long.")
            process = False
        if args[1] not in city_list:
            await ctx.channel.send("ugh what did you put in? That city doesn't exist... idiot.")
            process = False
        if process:
            str_command = "INSERT INTO " + mysql_table + " VALUES (\'" + str(args[0]) + "\',\'" + str(args[1]) + "\'," + args[2] + "," + args[3] + ");" 
            print(str_command)
            cur.execute(str_command)
            db.commit()
            await ctx.channel.send("Gym Added!")
    else:
        await ctx.channel.send("Uh, WTF do you think you're doing?")
    db.close()

@bot.command(pass_context=True)
async def delgym(ctx, *args):
    db = MySQLdb.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,db=mysql_db)
    cur = db.cursor()
    if ctx.message.author.id in admins:
        str_cmd = "DELETE FROM " + mysql_table + " WHERE gymname = \"" + str(args[0]) + "\";"
        print(str_cmd)
        cur.execute(str_cmd)
        db.commit()
    else:
        print(ctx.message.author.id)
    db.close()
'''
@bot.command(pass_context=True)
async def testcmd(ctx, *args):
    e = discord.Embed(title="Test",url="http://google.com/",author="Brandon")
    await ctx.channel.send(embed=e)

@bot.event
async def on_message(msg):
    if msg.channel.name is None:
        print("No channel name: {}".format(msg))
    else:
        await bot.process_commands(msg)
    return None

Token=cfg['discord-token']

bot.run(Token)
