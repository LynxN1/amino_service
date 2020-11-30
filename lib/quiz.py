import amino


def quiz(client, com_id: str, quiz_link: str):
    questions_list = []
    answers_list = []

    while True:
        email = input("Email: ")
        password = input("Password: ")
        try:
            client.login(email=str(email), password=str(password))
            break
        except amino.exceptions.ActionNotAllowed:
            input("[quiz]: Wait to VPN...")
        except amino.exceptions.FailedLogin:
            print("[quiz]: Failed Login")
        except amino.exceptions.InvalidAccountOrPassword:
            print("[quiz]: Invalid account or password.")
        except amino.exceptions.InvalidPassword:
            print("[quiz]: Invalid Password")
        except amino.exceptions.InvalidEmail:
            print("[quiz]: Invalid Email")

    subclient = amino.SubClient(comId=com_id, profile=client.profile)

    quiz_id = subclient.get_from_code(str(quiz_link.split('/')[-1])).objectId

    quiz_info = subclient.get_blog_info(quizId=quiz_id).json
    quiestions = quiz_info["blog"]["quizQuestionList"]
    total_questions = quiz_info["blog"]["extensions"]["quizTotalQuestionCount"]

    for x, question in enumerate(quiestions, 1):
        print(f"[quiz][{x}/{total_questions}]: Choosing the right answer...")
        question_id = question["quizQuestionId"]
        answers = question["extensions"]["quizQuestionOptList"]
        for answer in answers:
            answer_id = answer["optId"]
            subclient.play_quiz(quizId=quiz_id, questionIdsList=[question_id], answerIdsList=[answer_id])
            latest_score = subclient.get_quiz_rankings(quizId=quiz_id).profile.latestScore
            if latest_score > 0:
                print(f"[quiz][{x}/{total_questions}]: Answer found!")
                questions_list.append(question_id)
                answers_list.append(answer_id)

    if "quizInBestQuizzes" in quiz_info["blog"]["extensions"]:
        for i in range(2):
            subclient.play_quiz(quizId=quiz_id, questionIdsList=questions_list, answerIdsList=answers_list, quizMode=i)
    else:
        subclient.play_quiz(quizId=quiz_id, questionIdsList=questions_list, answerIdsList=answers_list, quizMode=0)

    print(f"[quiz]: Passed the quiz!")
    print(f"[quiz]: Score: {subclient.get_quiz_rankings(quizId=quiz_id).profile.highestScore}")
