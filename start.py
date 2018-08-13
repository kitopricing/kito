# Feel free to modify the code. THIS IS A CHATBOT OPEN TO COLLABORATION. You can modify the script of this chatbot freely
# Once a week, the code is pushed in production


# Use BOTSAY to send a message to a user
# Use USER to use the object USER in an INTERACTION
# Use STATE to change the STATE of an interaction
# Use USERDICT to have access to all info related to a USER
# Use INBOX to read all unread messages
# Use CLR_INBOX to clear all unread messages
# Use INTER_CALLS to know the number of times an interactions has been called
# Use LAUNCH to launch any INTERACTION to any user



from question import Question

# -------------------------------------------------------------------------------------------------------------------


INTERACTION ProcessSpontaneous
    INPUT  user
        

    USEFULNESS:
        # This part define when the priority of the interaction when this interaction added in the "Possible Interaction" pool
        if INBOX[USER]:
            return 2.0
        else:
            return 0.0

    EXECUTE:
        # This part define the states of the interaction

        START_STATE
            STATE = 'process'

        STATE_DEF 'process'
            if INBOX[USER] and USER.s_greeted_by_kito is True:
                if INBOX[USER][-1].text == "poke":
                    pass
                else:
                    infos = {}
                    minsize = 100
                    for msg in INBOX[USER]:
                        minsize = min(minsize, len(msg.text))
                        results = corpus.process(msg.text)
                        infos.update(corp_get(results, 'name')) # This part in the NLP detection using standard templates + the templates in the templates.txt
                        infos.update(corp_get(results, 'help')) # This part in the NLP detection using standard templates + the templates in the templates.txt
                        infos.update(corp_get(results, 'sentiment')) # This part in the NLP detection using standard templates + the templates in the templates.txt
                        infos.update(corp_get(results, 'question')) # This part in the NLP detection using standard templates + the templates in the templates.txt
                        infos.update(corp_get(results, 'tone')) # This part in the NLP detection using standard templates + the templates in the templates.txt

                    if 'question' in infos:
                        if infos['question'] == 'true' and infos['question_score'] > 0.8:
                            LAUNCH_INTERACTION(WaitQuestion(BOT, USER))
                            CLR_INBOX(USER)
                            STATE = 'success'
                            return

                    if 'help' in infos:
                        if infos['help'] == 'true' and infos['help_score'] > 0.8:
                            BOTSAY(USER, "Type 'ask question' in order to ask question.  If you don't like my chat, please contribute to my code here: https://github.com/kitopricing/kito")
                            CLR_INBOX(USER)
                            STATE = 'success'
                            return

                    if 'tone' in infos:
                        if infos['tone'] == 'stopspamming' and infos['tone_score'] > 0.8:
                            BOTSAY(USER, lingua.ok())
                            CLR_INBOX(USER)
                            # This will have a direct effect on the Silent interaction
                            USER.s_time_of_last_message = str(datetime.now() - timedelta(hours=48))
                            STATE = 'success'
                            return

                    if 'name' in infos:
                        if infos['name_score'] > 0.99 and minsize > 100:  # 0.4 to too much, do not even recognize "My name is Bob"
                            int = AskName(BOT, USER)
                            int.state = 'wait for answer'
                            int.time_asked = datetime.now()
                            LAUNCH_INTERACTION(int)
                            STATE = 'success'
                            return

                    answer = sa.is_general_questionkito(INBOX[USER][-1].text)
                    if answer:
                        BOTSAY(USER, answer)
                    else:
                        BOTSAY(USER, lingua.i_dont_understand_kito())
                        BOTSAY(USER, "Remember: Type 'ask question' if you have a question. or 'menu' to go to the menu.")

            elif INBOX[USER] and USER.s_greeted_by_kito is not True:
                QUERE_INTERACTION(WelcomeNewUser(BOT, USER))
            CLR_INBOX(USER)
            STATE = 'success'

        STATE_DEF 'success'
            if USER.s_greeted_by_kito is True:
                LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'
            RESETTING_INTERACTION

        STATE_DEF 'end'
            pass
# -------------------------------------------------------------------------------------------------------------------


INTERACTION WelcomeNewUser
    INPUT  user

    USEFULNESS:
        if USER.s_greeted_by_kito:
            return 0.0
        else:
            return 3.0

    EXECUTE:

        START_STATE
            STATE = 'greet'

        STATE_DEF 'greet'
            BOTSAY(USER, "Hello! I'm Kito. The nEOS expert. I'm an opensource chatbot. You can ask me any question and I'll check how I can help.")
            BOTSAY(USER, "Thanks for reaching the pricing 24/7 help desk")
            BOTSAY(USER, "Type 'help' or 'menu' to go to the menu. Type 'ask question' to ask a question to me")
            USER.s_greeted_by_kito = True # All attributes stating with "s_" for a user will be shared accross all  servers (meaning all bots created)
            STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            LAUNCH_INTERACTION(AskPassword(BOT, USER))
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -------------------------------------------------------------------------------------------------------------------


INTERACTION AskPassword
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if INTER_CALLS == 0:
            # This interaction never ran before for this user
            return 0.9
        else:
            if TIME_SINCE_LAST_CALL > a_week:
                return 0.0
            elif TIME_SINCE_LAST_CALL > a_day:
                return 0.0
            else:
                return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:
                BOTSAY(USER, "Could you please introduce the password of this App?")
            else:
                BOTSAY(USER, "I would highly appreciate if you can give me the password of this app!")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    infos.update({'text': msg.text})

                if ('text' in infos and "banana" in infos['text']) or ('text' in infos and "Banana" in infos['text']):
                    BOTSAY(USER, lingua.thanks())
                    USER.accepted_by_kito = True
                    CLR_INBOX(USER)
                    STATE = 'success'
                else:
                    BOTSAY(USER, "Password not correct. Sorry mate!")
                    CLR_INBOX(USER)

            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            LAUNCH_INTERACTION(AskName(BOT, USER))
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            ADD_POSSIBLE(WelcomeNewUser(BOT, USER))
            USER.s_greeted_by_kito = None
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION AskName
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if USER.s_name:
            return 0.0
        elif not LAUNCHES:
            # We don't know the name and this interaction never ran before
            return 0.5
        elif TIME_SINCE_LAST_CALL < 60*10.0:
            # We still don't know the name but apparently we already asked without success
            return 0.0
        else:
            return 0.5

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:  # because we have to go thru the state "None" before
                BOTSAY(USER, lingua.whats_your_name())
            elif STATECALLS <= 2:  # because we have to go thru the state "Failure" "None" before
                BOTSAY(USER, "You haven't told me your name yet?")
            elif STATECALLS <= 3:
                BOTSAY(USER, "You still don't want to tell me your name?")
            elif STATECALLS <= 4:
                BOTSAY(USER, "I guess I will never get to know your name...")
                # "Do you have privacy concerns???"
            else:
                BOTSAY(USER, "As I don't know your name, I will call you Mr. Pink.")
                USER.s_name = 'Mr. Pink'
                STATE = 'success'

            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'someone'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'logic'))
                    if ' ' not in msg.text:
                        infos.update({'any': msg.text,
                                      'any_score': 1})
                    infos.update(corp_get(results, 'any'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                if 'someone' in infos and 'logic' in infos and infos['logic'] == "negative":
                    BOTSAY(USER, "haha! trying to test me? I'm smarter than you think... So... What's your name then?")
                    STATE = 'wait for answer'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
                if 'someone' in infos or 'any' in infos:
                    answer = sa.get_gender_based_on_name(infos['someone'] if 'someone' in infos else infos['any'])
                    if (infos['someone'] if 'someone' in infos else infos['any']).lower() == "kito":
                        BOTSAY(USER, "Really?'{}'!. Just like me?. Are you sure I got it right?".format(
                            infos['someone'] if 'someone' in infos else infos['any']))
                        STATE = 'wait for confirmation'
                        self.time_asked = datetime.now()
                        CLR_INBOX(USER)
                        USER.s_name = "Kito"
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        else:
                            ADD_AGAIN_POSSIBLE(AskGender(BOT, USER))
                        return
                    if answer and answer['samples'] < 1000:
                        BOTSAY(USER, "Really?'{}'!. That's unusual. Are you sure I got it right?".format(infos['someone'] if 'someone' in infos else infos['any']))
                        STATE = 'wait for confirmation'
                        self.time_asked = datetime.now()
                        CLR_INBOX(USER)
                        USER.s_name = infos['someone'] if 'someone' in infos else infos['any']
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        else:
                            ADD_AGAIN_POSSIBLE(AskGender(BOT, USER))
                        return
                    elif ('someone_score' in infos and infos['someone_score'] < 0.00001) or ('any' in infos and infos['any_score'] < 0.00001):
                        BOTSAY(USER,
                                     "It's the first time I meet someone named '{}'!. Are you sure I got it right?".format(
                                         infos['someone'] if 'someone' in infos else infos['any']))
                        STATE = 'wait for confirmation'
                        self.time_asked = datetime.now()
                        CLR_INBOX(USER)
                        USER.s_name = infos['someone'] if 'someone' in infos else infos['any']
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        return
                    USER.s_name = infos['someone'] if 'someone' in infos else infos['any']
                    BOTSAY(USER, lingua.ok())
                    BOTSAY(USER, "Nice to meet you, {}!".format(USER.s_name))
                    CLR_INBOX(USER)

                    if answer is not None and answer['accuracy'] > 95:
                        USER.gender = answer['gender']
                    elif answer is not None and answer['accuracy'] > 80:
                        if answer['gender'] == 'female':
                            BOTSAY(USER, "I know a few {} named like that, but also a {}.".format("girls", "boy"))
                        else:
                            BOTSAY(USER, "I know a few {} named like that, but also a {}.".format("boys", "girl"))
                        LAUNCH_INTERACTION(AskGender(BOT, USER))
                    else:
                        BOTSAY(USER, "mmm... I don't know any people named like that.")
                        if answer is not None and answer['accuracy'] > 95:
                            USER.gender = answer['gender']
                        else:
                            LAUNCH_INTERACTION(AskGender(BOT, USER))
                    STATE = 'success'
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                    infos.update(corp_get(results, 'someone'))

                if 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'true':
                    BOTSAY(USER, "ok! got it! ... then,  nice to meet you, {}!".format(USER.s_name))
                    ADD_POSSIBLE(AskGender(BOT, USER))
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
                elif 'someone' in infos and 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                    USER.s_name = infos['someone']
                    BOTSAY(USER, "Ok! Understood! Nice to meet you, {}!".format(USER.s_name))
                    ADD_POSSIBLE(AskGender(BOT, USER))
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
                elif 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                    BOTSAY(USER, "Ok! What's your name then?")
                    STATE = 'wait for answer'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
                else:
                    BOTSAY(USER, "I'm not sure I get it")
                    STATE = 'wait for confirmation'
                    self.time_asked = datetime.now()
                    CLR_INBOX(USER)
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                BOTSAY(USER, " '{}'! Did I understand your name correctly?".format(USER.s_name))
                self.time_asked = datetime.now()
                self.clean_state_calls_with_msg()
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            ADD_POSSIBLE(AskTeam(BOT, USER))
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION AskGender
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if USER.gender:
            return 0.0
        else:
            return 0.9

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            BOTSAY(USER, "Are you male or female?")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'gender'))
                    infos.update(corp_get(results, 'tone'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.0:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                if 'gender' in infos and infos['gender_score'] > 0.0:
                    USER.gender = infos['gender']
                    BOTSAY(USER, lingua.ok())
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 3:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ----------------------------------------------------------------------------------------------------------------------

INTERACTION Silent
    """The goal here is no avoid spamming the user when he doesn't want to talk with us.
    If the user wanna chat and is really reactive, then, a proactive discussion might be a good idea,
    if not, it might be good to talk only when necessary and avoid that the user feels spammed"""
    INPUT  user
        self.start = None

    USEFULNESS:

        if 's_time_of_last_message' not in USERDICT:
            return 0.0
        if USER.s_time_of_last_message is None or not USER.s_time_of_last_message:
            return 0.0
        delta = (datetime.now() - datetime.strptime(str(USER.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
        if delta > a_week:
            # The user is completely silent, don't disturb him except it necessary
            return 1.2
        elif delta > a_day*4:
            # The user is completely silent for 2 days, don't disturb him except it necessary
            return 0.9
        elif delta > a_day:
            # The user is completely silent for 1 days, don't disturb him except it necessary
            return 0.8
        elif delta > 60 * 60:
            # The user is completely silent for 1 hour, don't disturb him except it necessary
            return 0.7
        elif delta > 60 * 5:
            # The user is completely silent for 5 min, don't disturb him except it necessary
            return 0.45
        else:
            return 0.0

    EXECUTE:
        START_STATE
            STATE = 'silent'
            self.start = datetime.now()

        STATE_DEF 'silent'
            if INBOX[USER]:
                STATE = 'success'
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            elif (datetime.now() - self.start).total_seconds() < 60.0 * 60.0:
                return
            else:
                STATE = 'success'

        STATE_DEF 'success'
            RESETTING_INTERACTION
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ----------------------------------------------------------------------------------------------------------------------


INTERACTION Breath
    """ Just wait a bit and slow the discussion a bit to make it more natural when needed"""
    INPUT  user
        self.start = None

    USEFULNESS:
        if USER.last_message_sent_to_user is not None and USER.last_message_sent_to_user >= datetime.now() - timedelta(seconds=2):
            return 1.5
        else:
            return 0.0

    EXECUTE:
        START_STATE
            STATE = 'silent'
            self.start = datetime.now()

        STATE_DEF 'silent'
            if (datetime.now() - self.start).total_seconds() < 3:
                return
            else:
                STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION AskTeam
    INPUT  user
        self.time_asked = None

    USEFULNESS:
        if USER.kito_is_PE:
            return 0.0
        else:
            return 0.9

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            BOTSAY(USER, "Are you a Pricing Engineer?")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.0:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                if 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'true':
                    USER.kito_is_PE = 1.0
                    BOTSAY(USER, lingua.ok())
                    BOTSAY(USER, "Even if you are from the pricing team, feel free to as me any question you want.")
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
                elif 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                    USER.kito_is_PE = 0.0
                    BOTSAY(USER, lingua.ok())
                    BOTSAY(USER, "Feel free to ask me any question you want.")
                    CLR_INBOX(USER)
                    STATE = 'success'
                    return
                else:
                    BOTSAY(USER, lingua.i_dont_understand())
                    CLR_INBOX(USER)
                    return

            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 3:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            LAUNCH_INTERACTION(WaitQuestion(BOT, USER))
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ----------------------------------------------------------------------------------------------------------------------


INTERACTION WaitQuestion
    INPUT  user
        self.time_asked = datetime.now()
        self.time_conf_asked = datetime.now()
        self.query = None

    USEFULNESS:
        if USER.kito_is_PE:
            return 0.0
        else:
            return 0.9

    EXECUTE:

        START_STATE
            STATE = 'ask'

        STATE_DEF 'ask'
            if STATECALLS <= 1:
                BOTSAY(USER, "Ok, let me know what is the question you wanna ask to the pricing team?")
            elif STATECALLS <= 2:
                BOTSAY(USER, "Ok, let me know what is the question you wanna ask to the pricing team?")
            else:
                BOTSAY(USER, "Ok, let me know what is the question you wanna ask to the pricing team?")
            STATE = 'wait for answer'
            self.time_asked = datetime.now()

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > 60*5:
                BOTSAY(USER, "Ok, don't hesitate to come back to me later with a question via the menu...")
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update({'text': msg.text})
                    infos.update(corp_get(results, 'tone'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.9:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                        STATE = 'failure'
                        return

                self.query = Question(infos['text'], USER)
                BOTSAY(USER, "The question that will be sent to your pricing team is: " + str(self.query.question) + ". Do you confirm? (y/n)" )
                self.time_conf_asked = datetime.now()
                CLR_INBOX(USER)
                STATE = 'wait for confirmation'
                return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 3:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_conf_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.7:
                        BOTSAY(USER, lingua.dont_be_so_rude())
                        CLR_INBOX(USER)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1:
                    CLR_INBOX(USER)
                    if infos['boolean'] == "true":
                        STATE = 'success'
                        BOTSAY(USER, "Ok, understood! I'll investigate and come back to you in the next 5-10 min")

                        is_PE = lambda u: u.kito_is_PE and float(u.kito_is_PE) == 1.0
                        is_not_user = lambda u: u == USER
                        self.query.to_be_asked = SEARCH_IF(lambda u: is_PE(u) and is_not_user)
                        LAUNCH_INTERACTION(LoopToAll(BOT, self.query))

                    else:
                        STATE = 'failure'
                        BOTSAY(USER, "Ok! No probs")
                    CLR_INBOX(USER)
                    return
                else:
                    BOTSAY(USER, lingua.i_dont_understand())
                    CLR_INBOX(USER)
                    return
            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return
            if STATE == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            LAUNCH_INTERACTION(Breath(BOT, USER))
            STATE = 'end'
            self.time_asked = datetime.now()

        STATE_DEF 'failure'
            RESETTING_INTERACTION
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ----------------------------------------------------------------------------------------------------------------------


INTERACTION LoopToAll
    INPUT  query
        
        self.currently_asked = None
        self.tempuser = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'loop'

        STATE_DEF 'loop'
            if self.query.to_be_asked is not None and len(self.query.to_be_asked)>0 and self.query.to_be_asked[0] is self.query.user_asked:
                self.query.to_be_asked.pop(0)
                return
            elif self.query.to_be_asked is not None and len(self.query.to_be_asked) > 0 and self.query.to_be_asked[0] is not None:
                if self.tempuser is not self.query.to_be_asked[0]:
                    LAUNCH_INTERACTION(AskAnswer(BOT, self.query.to_be_asked[0], self.query))
                    self.tempuser = self.query.to_be_asked[0]
                    return
                else:
                    return
            else:
                STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION Breath2
    """ Just wait a bit and slow the discussion a bit to make it more natural when needed"""
    INPUT  user
        self.start = None

    USEFULNESS:
        if USER.last_message_sent_to_user is not None and USER.last_message_sent_to_user >= datetime.now() - timedelta(seconds=2):
            return 0.8
        else:
            return 0.0

    EXECUTE:
        START_STATE
            STATE = 'silent'
            self.start = datetime.now()

        STATE_DEF 'silent'
            if (datetime.now() - self.start).total_seconds() < 8:
                return
            else:
                STATE = 'success'

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# ---------------------------------------------------------------------------------------------------------------------


INTERACTION AskAnswer
    INPUT  user, query
        
        
        self.time_asked = None
        self.time_conf_asked = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'ask_answer'

        STATE_DEF 'ask_answer'
            BOTSAY(USER, "I just received a question from a user named '" + str(self.query.user_asked.s_name) + "': "+ str(self.query.question) + ". Do you know the answer? Yes/No/Start Chatting")
            STATE = 'wait for confirmation'
            self.time_conf_asked = datetime.now()

        STATE_DEF 'wait for confirmation'
            if (datetime.now() - self.time_conf_asked).total_seconds() > 60*10:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'chatting'))
                if 'chatting' in infos and infos['chatting_score'] > 0.1:
                    if infos['chatting'] == 'true':
                        if USER.chatting is not True and self.query.user_asked.chatting is not True:
                            USER.chatting = True
                            self.query.user_asked.chatting = True
                            self.query.user_reply = USER
                            self.query.chatting = True
                            BOTSAY(USER, "You are now chatting with the other neighbour who ask the question, type 'end' to stop the discussion")
                            BOTSAY(self.query.user_asked, "You are now chatting with someone in your area who can help you, type 'end' to stop the discussion")
                            LAUNCH_INTERACTION(UserChat(BOT, USER, self.query.user_asked, self.query))
                            LAUNCH_INTERACTION(UserChat(BOT, self.query.user_asked, USER, self.query))
                            STATE = 'success'
                        else:
                            BOTSAY(USER, "It seems the user is already chatting with someone else so I assume he found the help he wanted. Thanks anyway.")
                            STATE = 'failure'
                        CLR_INBOX(USER)
                        return
                if 'boolean' in infos and infos['boolean_score'] > 0.1:
                    if infos['boolean'] == "true":
                        if not self.query.answered:
                            STATE = 'wait for answer'
                            self.time_asked = datetime.now()
                            BOTSAY(USER, "Ok, What is the response?")
                            self.query.answered = True
                            self.query.user_reply = USER
                        else:
                            STATE = 'success'
                            BOTSAY(USER, "Thanks! But " + self.query.user_reply.s_name +" took the job")
                    else:
                        STATE = 'success'
                        BOTSAY(USER, "Ok! Maybe next time....")
                    CLR_INBOX(USER)
                    return

            if INBOX[USER]:
                LAUNCH_INTERACTION(ProcessSpontaneous(BOT, USER))
                return

            if STATE == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE == 'ask_answer'
                return

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                  infos.update({'text': msg.text})

                if 'text' in infos:
                    BOTSAY(USER, lingua.ok())
                    BOTSAY(self.query.user_asked, "Someone has a positive reply to your request: " + str(infos['text']) + ". Don't hesitate to relaunch a question any time.")

                CLR_INBOX(USER)
                STATE = 'success'
                return

            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE == 'ask_answer'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            self.query.to_be_asked = None
            STATE = 'end'

        STATE_DEF 'failure'
            REMOVE_POSSIBLE(self)
            self.query.to_be_asked.pop(0)
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------


INTERACTION UserChat
    INPUT  user, other_user, query
        
        
        
        self.time = None

    USEFULNESS:
        return 0.0

    EXECUTE:

        START_STATE
            STATE = 'discussion'
            self.time = datetime.now()

        STATE_DEF 'discussion'
            if (datetime.now() - self.time).total_seconds() > 60 * 60 * 48 or self.query.chatting is False:
                BOTSAY(USER, "Ok, the discussion with the other user will now end.")
                BOTSAY(self.other_user, "The other user left. Sorry. You are back to the main chatbot now.")
                STATE = 'success'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'stopdiscussion'))
                if 'stopdiscussion' in infos and infos['stopdiscussion_score'] > 0.2:
                    if infos['stopdiscussion'] == 'true':
                        self.query.chatting = False
                        CLR_INBOX(USER)
                        return

            if INBOX[USER]:
                BOTSAY(self.other_user, ">>>" + ''.join(str(elem.text) for elem in INBOX[USER]))
                CLR_INBOX(USER)
                return

            if STATE == 'discussion' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                return

        STATE_DEF 'wait for answer'
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                BOTSAY(USER, lingua.you_must_be_busy())
                STATE = 'failure'
                return

            elif INBOX[USER]:
                infos = {}
                for msg in INBOX[USER]:
                    infos.update({'text': msg.text})

                if 'text' in infos:
                    BOTSAY(USER, lingua.ok())
                    BOTSAY(self.query.user_asked, "Here is what I believe is the answer to your question: " + str(infos['text']))

                CLR_INBOX(USER)
                STATE = 'success'
                return

            if STATE == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                STATE = 'ask'
                return

        STATE_DEF 'success'
            REMOVE_POSSIBLE(self)
            self.query.user_asked.chatting = False
            self.query.user_reply.chatting = False
            self.query.chatting = False
            self.query.answered = True
            STATE = 'end'

        STATE_DEF 'end'
            pass
# -----------------------------------------------------------------------------------------------------------------------

