#!/usr/local/bin/python3

## First, classes. Scroll down to see main program
### (not sure how to make other cell's content visible)

g_DEBUG = False # will print out a bunch of messages
g_PATHQUESTIONFILE = "./Questions/allquestions.txt" # path to question text file (for now assume only one)

#import sys
import random

# My own exception class
class RestartQuiz(Exception):
    def __init__(self, message):
        self.message = message

# Question
class QuestionCard:

    def __init__(self, question, answers, categories, isMultChoice):
        self.quest = question
        self.answ = answers # list
        self.categ = categories
        # list index identifying the position of the correct alternative
        # will be set by the printAnswersInRandomisedOrder() function
        # (only relevant for multiple-choice questions)
        self.idx_random_correct = -99
        self.letters = 'ABCDEFGHIJKLMNOP'
        self.mult_choice = isMultChoice

    def printAnswersInRandomisedOrder(self):
        indices = list(range(len(self.answ)))
        indices_rand = indices
        random.shuffle(indices_rand)
        print("Answer alternatives: ")
        idx_count = 0
        idx_correct = -99
        for idx_rand in indices_rand:
            print("{}: {}".format(self.letters[idx_count], self.answ[idx_rand]))
            if idx_rand == 0:
                idx_correct = idx_count
            idx_count += 1

        return idx_correct

    def ask(self, retry = False):
        print ("")
        # Ask question
        if not retry:
            print(self.quest)
            print("----------------------------------")

        # Give answer (non-multiple-choice) or ask for answer alternatives (multiple-choice)
        if not retry:
            # If more than one answer, interpret as multiple-choice question, and print answer alternatives in randomised order
            if self.mult_choice:
                self.idx_random_correct = self.printAnswersInRandomisedOrder()
            # else, prompt for answer
            else:
                prompt_ans = input("Hit any key to see the answer: ")
                print("Answer: ")
                for ans_line in self.answ:
                    print("       {}".format(ans_line))

        # If multiple-choice, prompt for user answer
        if self.mult_choice:
            try:
                user_answer = str(input("*** Please enter your answer: ")).upper()
                assert user_answer in self.letters[:len(self.answ)]
            except AssertionError:
                print("ERROR: Your answer is not among the accepted ones. Please try again: ")
                return self.ask(True)
            if user_answer == self.letters[self.idx_random_correct]:
                print("\nYou gave answer {}, which is correct! Good job!".format(user_answer))
            else:
                print("\nYou gave answer {0}, which is not correct... Sorry. The correct answer is {1}".format(user_answer, self.letters[self.idx_random_correct]))


        cont = str(input("\nHit 'Q' to quit. Hit any other key to continue: ")).upper()
        if cont == "Q":
            return False

        return True

    def show(self):
        print("Question: {}".format(self.quest.replace("Q:", "")))
        print("Answer(s): ")
        for idx,ans in enumerate(self.answ):
            print("{}: {}".format(self.letters[idx], ans))
        print("Categories (tags): {}".format(','.join(self.categ).lstrip(',')))

# Class for reading questions from textfile, making QuestionCards
# and putting them into a Deck
class QuestionMaker:

    path_questionfile = ""

    def __init__(self, path_questionfile):
        self.path_questionfile = path_questionfile

    def makeQuestionCards(self, rawlines_questions):
        # make QuestionCards out of the raw lines of questions from the question file.

        # the question file must be organized in questions with lines
        #  1) "Q: ..:", 2) "A: ...[possibly several lines]" and 3) "C: ...".

        list_QuestionCards = []
        while rawlines_questions:
            # The categories
            line_categories = rawlines_questions.pop()
            categories = [""]
            if line_categories:
                categories = line_categories.split(",")
                for idx_categ in range(len(categories)):
                    # remove duplicated spaces
                    categories[idx_categ] = ' '.join(categories[idx_categ].split())
                    # make sure no category is empty
                    if categories[idx_categ] == "":
                        raise Exception("QuestionFileFormatError: Empty category found among categories. They should be given comma-separated. Line in file = {}".format(line_categories))
                categories[0] = categories[0].replace("C: ", "")

            # The answers -- pop line until we hit "A: " which indicates the first line of the answers
            lines_answers = []
            if rawlines_questions[-1].startswith("A:"):
                lines_answers = [rawlines_questions.pop()]
            else:
                while not rawlines_questions[-1].startswith("A:"):
                    lines_answers.append(rawlines_questions.pop())
                lines_answers.append(rawlines_questions.pop()) # append the last line (the line starting w/ "A:")

            # put them in the correct order
            lines_answers.reverse()

            # If ";" in answer, assume it's multiple choice
            isMultChoice = False
            if ";" in str(lines_answers):
                isMultChoice = True
                answers = lines_answers[0].split(";")
                if len(answers) < 1:
                    raise Exception("QuestionFileFormatError: No answers found after 'A:' in question file! You should give them ';'-separated, the first one should be the correct answer. Answer line(s) = {}".format(lines_answers))
            else:
                answers = lines_answers

            for idx_ans in range(len(answers)):
                # remove duplicated spaces
                line_ans = answers[idx_ans]
                if isMultChoice:
                    answers[idx_ans] = ' '.join(line_ans.split())
                # but if not-multiple choice, keep new lines
                else:
                    answers[idx_ans] = '\n'.join(' '.join(line.split()) for line in line_ans.split('\n'))
                # assure no answer is empty
                if answers[idx_ans] == "":
                    raise Exception("QuestionFileFormatError: Empty answers found among answer alternatives. Answer list = {}".format(answers))

            # Finally, the question
            line_question  = rawlines_questions.pop()

            # sanity check
            if not (line_question.startswith("Q:") and lines_answers[0].startswith("A:") and line_categories.startswith("C:")):
                raise Exception("QuestionFileFormatError: Question file at {0} doesn't have correct format 'Q: .., A: .. C: '! \n You have question line: {1} \n     answer line(s): {2} \n  and categories line: {3}".format(self.path_questionfile, line_question, lines_answers, line_categories))

            answers[0] = answers[0].replace("A: ", "") # remove the "A: " now

            # print("DEBUG basically there, now we have \nquestion = {0} \nanswers = {1}".format(line_question, answers))

            # Make the question card, append to list of question cards
            qCard = QuestionCard(line_question, answers, categories, isMultChoice)
            list_QuestionCards.append(qCard)
        return list_QuestionCards

    def getListOfQuestionCards(self):
        # Open file, get lines as list
        with open(self.path_questionfile) as file_questions:
            rawlines_questions = list(filter(None, (line.rstrip() for line in file_questions)))

        # Interpret "#" as comment
        rawlines_questions = [line for line in rawlines_questions if not line.startswith("#")]

        list_QuestionCards = []
        try:
            list_QuestionCards = self.makeQuestionCards(rawlines_questions)
        except Exception as error:
            print(error)
        except:
            # default case - print message and re-raise exception
            print("Unexpected error:", sys.exc_info()[0])
            raise

        return list_QuestionCards


# Deck of QuestionCards
class Deck:

    def __init__(self):
        # the deck of cards, implemented as dictionary, {0: QuestionCard, 1: QuestionCard...}
        self.library = {}
        self.categs = []

    # Override len() and index operators, so the Deck itself can be treated like a dictionary
    def __len__(self):
        return len(self.library)

    def __getitem__(self, idx):
        return self.library[idx]

    def load(self, path_to_questionfile, categories = None):
        # Fill Deck with QuestionCards with the help of QuestionMaker
        # By default, fill with all questions
        # TODO: implement to fill with only certain category
        qMaker = QuestionMaker(path_to_questionfile)
        listOfQuestionCards = qMaker.getListOfQuestionCards()
        if len(self.library) == 0:
            id = 0
            for qCard in listOfQuestionCards:
                self.library[id] = qCard
                id += 1
        else:
            print("You're trying to add to a deck which isn't empty. Is that what you want to do? If yes, implement it :)")

        if g_DEBUG:
            print("You have now collected question cards for this deck. The cards are: ")
            self.dumpQuestions()

    def dumpQuestions(self):
        for key_card in self.library:
            print("\n*** Question {}: ".format(key_card+1))
            self.library[key_card].show()

    def dumpCategories(self):
        """ Loop over QuestionCards to find all categories, list them numbered, return dictionary """
        categs = []
        for key_card in self.library:
            categs += [ca for ca in self.library[key_card].categ if ca not in categs]
            # categs_card = self.library[key_card].categ
            # for categ in categs_card:
            #     if categ not in dict_categs.values():
            #         dict_categs[key_counter] = categ
            #         key_counter += 1
        # now we have list of categories, put this in a numbered fashion in a dictionary
        dict_categs = {i+1:categs[i] for i in range(len(categs))}# dictionary with structure {1: 'categoryA', 2:'categoryB',... }
        # print it
        print("")
        for num_ca in dict_categs:
            print("{0}) {1}".format(num_ca, dict_categs[num_ca]))
        # return it
        return dict_categs

    def filterCateg(self, categories):
        # specialise the deck by removing cards which aren't tagged with the desired category
        lib_specialised = {key:self.library[key] for key in self.library if not set(self.library[key].categ).isdisjoint(categories)}
        if len(lib_specialised) < 1:
            raise RestartQuiz("*** ERROR in Deck::specialise >> ended up with empty deck. None of your categories {} exist!".format(categories))
        self.library = lib_specialised



# The QuizMaster that will run the quiz
class QuizMaster:

    def __init__(self, path_to_questionfile = g_PATHQUESTIONFILE):
        self.all_questions = Deck()
        self.all_questions.load(path_to_questionfile)
        if len(self.all_questions.library) < 1:
            raise ValueError("ERROR in QuizMaster::__init__ >> questions loaded, but deck empty!")

        self.categories = [""]     # dummy choice of categories, will be set by run()
        self.current_deck = self.all_questions # set to all_questions by default, will be filtered in run() if certain categories given

        # List of items in menu. Make sure "Quit" is the last item
        self.menu = ["Take quiz", "Enter new question", "Quit"]


    def showMenu(self):
        print("\nWhat do you want to do?")

        for idx,item in enumerate(self.menu):
            print("{}: {}".format(idx+1, item))


    def run(self):

        self.showMenu()

        choice = len(self.menu) # default = quit as safety
        choice_OK = False

        while not choice_OK:
            try:
                choice = int(input("Please enter your choice: "))
                assert 1 <= choice <= len(self.menu)
                choice_OK = True # should only be reached if no exceptions thrown
            except AssertionError:
                print("Choice not recognized (did you enter a number in the menu?) -- please try again.")
            except ValueError:
                print("Choice doesn't appear to be an integer. Please try again.")
            # any other exceptions
            except Exception as exception:
                print("Built-in exception raised: {}".format(exception))


        if choice == len(self.menu):
            print("\n*** Exiting program. Good  bye. ")
            # should maybe exit explicitly, but for not just do nothing. (Don't want "kernel has died" message...)
            #exit()
        else:
            # hard-coded choice cases for now
            if choice == 1:
                successfully_taken_quiz = False
                while not successfully_taken_quiz:
                    try:
                        self.takeQuiz()
                        # this is only reached if Exception is not thrown
                        successfully_taken_quiz = True
                    except RestartQuiz as exc_restartquiz:
                        print("*** ERROR in takeQuiz :: RestartQuiz exception with message {}".format(exc_restartquiz.message))
                        print("*** Let's try again")
                    # any other exceptions
                    except Exception as exception:
                        print("*** ERROR in takeQuiz :: some other built-in exception: {}".format(exception))

            elif choice == 2:
                print("This feature is not implemented yet... Sorry.")



    def takeQuiz(self):
        print("\nYou have chosen to take the quiz.")
        print("Do you want to take it only with certain categorie(s) (subject(s))? Here are the list of categories: \n")
        dict_categs = self.all_questions.dumpCategories()
        categ_nums = []
        categ_nums = str(input("\nEnter the number of the categories you want to include in the quiz (comma-separated). \nIf you want to take it with all categories, just press enter:"))
        if categ_nums:
            # remove whitespace from string of category numbers
            categ_nums = ''.join(categ_nums.split())
            # make list with numbers corresponding to categories
            categ_nums = categ_nums.split(",")
            # sanitize: check that given input is actually numbers
            int_categ_nums = []
            for categ_num in categ_nums:
                try:
                    num = int(categ_num)
                    int_categ_nums.append(num)
                except ValueError as error:
                    errmsg = str(error)
                    # self.takeQuiz(choice)
                    raise RestartQuiz("*** ERROR in QuizMaster::takeQuiz :: couldn't identify your list of numbers as numbers.")
            # check that given numbers were actually in the list
            for num in int_categ_nums:
                if num not in range(1, 1+len(dict_categs)):
                    raise RestartQuiz("*** ERROR in QuizMaster::takeQuiz :: At least one of the numbers you gave were not in the list of categories. You gave number {} which isn't in the list. Trying again. ".format(num))
                    # self.takeQuiz()


            # except Exception as error:
            #     print(error)
            #     self.takeQuiz(choice)

            # make list of categories (i.e. the actual categories, not their corresponding numbers)
            categs = [dict_categs[i] for i in dict_categs if i in int_categ_nums]

            print("You have chosen to take the quiz with categories:\n")
            for categ in categs: print("* {}".format(categ))

            # now filter out not chosen categories from the currently full deck
            self.current_deck.filterCateg(categs)

        else:
            # don't do anything, keep default current_deck = all questions
            print("You have chosen to take the SUPERQUIZ with all the categories included. Good luck, you're gonna need it!")

        # Run the quiz by asking questions until user terminates it
        print("\n*** Starting quiz. Questions coming up! \n")

        while self.askQuestion():
            pass

        # Should only end up here if user prompted a quit
        print("\n*** You have chosen to end the program. Good bye!")


    def askQuestion(self):
        if g_DEBUG: print("Inside QuizMaster::askQuestion()")

        # Get random card from deck, ask its question.
        # The 'ask' method returns True or False, where False means
        # the user wants to quit the program (not answer any more questions)
        rand_key = random.choice(list(self.current_deck.library.keys()))
        return self.current_deck[rand_key].ask()

    def addQuestion(self):
        if g_DEBUG: print("Inside QuizMaster::addQuestion()")


#======= Main program
if __name__ == '__main__':

    print("\nWelcome to the quizMe program!")

    #quizMaster = QuizMaster("/Users/edvinsidebo/code-projects/quizMe/Questions/testfilequestions.txt")
    quizMaster = QuizMaster(g_PATHQUESTIONFILE)
    quizMaster.run()
