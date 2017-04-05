import os
import time
from slackclient import SlackClient


# sae-slackbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

#help command
HELP_COMMAND = "help"

#parrot command, might eventually be able to message the bot in a private message telling it what channel to say it in?
PARROT_COMMAND = "say"

#eve commands, anything to do with eve stuff
EVE_COMMAND = "eve"
EVE_DIED_COMMAND = "died"
EVE_KILLED_COMMAND = "killed"
EVE_DEATHS_COMMAND = "deaths"
EVE_KILLS_COMMAND = "kills"
EVE_ADDUSER_COMMAND = "adduser"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Wat? I don't get it. Use the *" + HELP_COMMAND + \
               "* command to figure out what the fuck you're tryna say."

    if command.startswith(HELP_COMMAND):#if help
		command = command[5:] #substring the command for easier use in finding out what to do subsequently
        response = "Heres a list of commands: help, say, eve.\nuse *help xxxx* to learn more about a command, where xxxx is the command name."
		if command.startswith(EVE_COMMAND)#if theyre asking for help with eve specifically
			response = "list of subcommands for the eve command:\ndied: use *eve died xxxx* to record a player death, where xxxx is the player name.\n" +
			"killed: use *eve killed xxxx* to record a group kill, where xxxx is the name of the ship that the group killed.\n" +
			"deaths: use *eve deaths* to display the total group death count, or *eve deaths xxxx* to display a specific players death count.\n" +
			"kills: use *eve kills* to display group kill list.\n" + 
			"adduser: use *eve adduser xxxx* to add a new eve user to be able to track deaths and kills, where xxxx is user name."
	
    if command.startswith(PARROT_COMMAND):#if say
		response = "Haven't written this command yet lul. git rekt"
	
	if command.startswith(EVE_COMMAND):#if eve
		command = command[4:] #substring the command for easier use in finding out what to do subsequently
		response = "FRIGATE FLEET TUESDAYS BOIIIIIII. If you actually wanna do something with this command then try *help eve*."
		if command.startswith(EVE_DIED_COMMAND)
			command = command[5:]#further substring the command for use
			
			#for line in blah: if command.startswith() see below
			#write to file
			response = "Damn boi yall suck. The selected player's death count  has been updated."
		if command.startswith(EVE_KILLED_COMMAND)
			command = command[7:]#further substring the command for use
			if command:
				with open("eve_group_kills.txt", "a") as group_kills_file:
					group_kills_file.write(command)
					
				response = "Fuckin GF dude, kill has been logged."
			else
				response = "You obviously didnt kill anything if you cant even remember their name u fukin dingus."
		if command.startswith(EVE_DEATHS_COMMAND)
			command = command[7:]#further substring the command for use
			
			if command:
				with open("eve_players.txt", "r") as eve_players:
					for line in eve_players:
						if (line == command)
							with open("" + command + "deaths.txt", "r") as user_death_file:
								deathcount = user_death_file.read()
							
							response = command + "has died " + deathcount + "times with the group."
						else
							response = "that player don't exist homie."
			else
				with open("eve_group_deaths.txt", "r") as group_deaths_file:
					deathcount = group_deaths_file.read()
				
				response = "Total number of deaths by all group members: " + deathcount
		if command.startswith(EVE_KILLS_COMMAND)
			command = command[7:]#further substring the command for use. This one is probably unneccessary because there is no subsequent task
			
			#open the file, read all of the data into the kills var, close the file
			with open("eve_group_kills.txt", "r") as group_kills_file:
				kills = group_kills_file.readlines()
			
			response = "Group kills:\n" + kills
		if command.startswith(EVE_ADDUSER_COMMAND)
			command = command[8:]#further substring the command for use.
			
			if command:
				with open("eve_players.txt", "a") as eve_players:
					eve_players.write(command)
			
				with open("" + command + "deaths.txt", "w") as newuser_death_file:
					newuser_death_file.write("0")
				
				response = "User has been added and files have been created for them!"
			else
				response = "please specify a user name if youre gonna use this command fam."
			#add user

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

###############################################################################################################################
#todo:
#
#test if startswith works with only start and not end(only if the substring doesnt work. command will look like the following)
#command.startswith(EVE_DIED_COMMAND, 4)
#test the newline char in the help command
#test the command = command[4:] line, if the command is eve killed the command should then just be killed
#test the multiline string
#create and test the eveplayers file, which means figure out how to write adduser
#test the string concatenation between response and killcount
#thoroughly test the adduser stuff. Have absolutely no idea what im doing there and the naming could be wrong and shit
#learn for line in things better to iterate through files
#
###############################################################################################################################
#
# dont mess with shit below this line too much lul
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("sae-slackbot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")