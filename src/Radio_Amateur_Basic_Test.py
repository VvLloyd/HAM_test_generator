import sys
import random
from PySide6.QtCore import QTimer, QElapsedTimer, Qt  # Using QElapsedTimer here
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QRadioButton, QGroupBox, QHBoxLayout, QButtonGroup, QGridLayout, QFrame
import math

class QuizApp(QWidget):
    def __init__(self, questions):
        super().__init__()

        self.questions = questions
        self.current_question_index = 0
        self.score = 0
        self.total_questions = len(questions) 

        self.correct_answer = None
        self.button_group = None

        # Timer for elapsed time
        self.elapsed_timer = QElapsedTimer()  # Use QElapsedTimer here
        self.elapsed_timer.start()  # Start the timer when the app is launched

        self.elapsed_time_label = QLabel()
        self.elapsed_time_label.setStyleSheet("font-size: 12px;")  # Make label text smaller
        self.elapsed_time_label.setAlignment(Qt.AlignCenter)

        # Initialize the UI
        self.init_ui()

    def init_ui(self):
        # Apply a global stylesheet with a larger font size
        self.setStyleSheet("""
            QLabel, QPushButton, QRadioButton {
                font-size: 18px;  /* Increase font size */
                font-family: Calibri;  /* Set font type */
            }
        """)

        self.layout = QGridLayout()

        # Question label
        self.french_question_label = QLabel(WordWrap=True, TextInteractionFlags=Qt.TextInteractionFlag(True), Alignment=Qt.AlignLeft)
        self.layout.addWidget(self.french_question_label, 1, 1, 1, 3)
        self.french_question_label.setBaseSize(100, 500)

        self.english_question_label = QLabel(WordWrap=True, TextInteractionFlags=Qt.TextInteractionFlag(True), Alignment=Qt.AlignLeft)
        self.layout.addWidget(self.english_question_label, 1, 5, 1, 3)
        self.english_question_label.setBaseSize(100, 500)
        
        # Add a separator between the french and english sections
        self.separator = QFrame(FrameShape=QFrame.VLine, FrameShadow=QFrame.Sunken)
        self.layout.addWidget(self.separator, 1, 4, 5, 1)  
        self.separator.setFixedWidth(20)     

        # Text labels located next to radio buttons
        self.french_answers = []
        self.english_answers = []
        self.french_radio_button_widget = []
        self.english_radio_button_widget = []
        self.french_radio_button_layout = []
        self.english_radio_button_layout = []
        for i in range(0, 4):
            self.french_radio_button_widget.append(QWidget())
            self.english_radio_button_widget.append(QWidget())
            self.french_radio_button_layout.append(QVBoxLayout(self.french_radio_button_widget[i]))
            self.english_radio_button_layout.append(QVBoxLayout(self.english_radio_button_widget[i]))

            self.french_radio_button_widget[i].setFixedWidth(40)
            self.english_radio_button_widget[i].setFixedWidth(40)
            
            self.french_answers.append(QLabel(WordWrap=True, TextInteractionFlags=Qt.TextInteractionFlag(True), Alignment=Qt.AlignVCenter))
            self.english_answers.append(QLabel(WordWrap=True, TextInteractionFlags=Qt.TextInteractionFlag(True), Alignment=Qt.AlignVCenter))
            #self.english_answers[i].setAlignment(Qt.AlignVCenter)

            self.layout.addWidget(self.french_radio_button_widget[i], 2+i, 1)
            self.layout.addWidget(self.english_radio_button_widget[i], 2+i, 5)
            self.layout.addWidget(self.french_answers[i], 2+i, 2, 1, 2)
            self.layout.addWidget(self.english_answers[i], 2+i, 6, 1, 2)

        # Correct answer label
        self.french_correct_answer_label = QLabel(WordWrap=True, TextInteractionFlags=Qt.TextInteractionFlag(True))     
        self.layout.addWidget(self.french_correct_answer_label, 6, 1, 1, 3)

        self.english_correct_answer_label = QLabel(WordWrap=True, TextInteractionFlags=Qt.TextInteractionFlag(True))
        self.layout.addWidget(self.english_correct_answer_label, 6, 5, 1, 3)

        # Score display
        self.score_label = QLabel(Alignment=Qt.AlignCenter)
        self.layout.addWidget(self.score_label, 10, 3, 1, 4)

        # Create a layout for the buttons at the bottom
        button_layout = QVBoxLayout()

        # Submit button
        self.submit_button = QPushButton("Soumettre / Submit")
        self.submit_button.clicked.connect(self.submit_answer)
        button_layout.addWidget(self.submit_button)

        # Next button
        self.next_button = QPushButton("Suivante / Next")
        self.next_button.clicked.connect(self.next_question)
        self.next_button.setEnabled(False)  # Initially disabled
        button_layout.addWidget(self.next_button)

        # Progress label to show the number of answered questions at the bottom
        self.progress_label = QLabel(f"Répondues - Answered: {self.current_question_index}/{self.total_questions}", WordWrap=True, Alignment=Qt.AlignCenter)        
        self.layout.addWidget(self.progress_label, 8, 3, 1, 4)

        # Add the button layout at the bottom
        self.layout.addLayout(button_layout, 9, 3, 1, 4)

        # Elapsed time label (small size)
        self.layout.addWidget(self.elapsed_time_label, 7, 3, 1, 4)

        self.setLayout(self.layout)
        self.setWindowTitle("Amateur Radio (Basic) Test - v1.0.0")
        self.setGeometry(100, 100, 1000, 500)

        # Start the timer to update the elapsed time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

        self.display_question()

    def remove_radio_buttons(self):
        # Loop through all items in the radio layout and remove the radio buttons
        for i in range(len(self.french_radio_button_layout)):
            item = self.french_radio_button_layout[i].itemAt(0)
            if item is not None:
                widget = item.widget()
                if isinstance(widget, QRadioButton):
                    widget.deleteLater()  # Safely remove the widget

        for i in range(len(self.english_radio_button_layout)):
            item = self.english_radio_button_layout[i].itemAt(0)
            if item is not None:
                widget = item.widget()
                if isinstance(widget, QRadioButton):
                    widget.deleteLater()  # Safely remove the widget

            self.french_radio_button_layout[i].update()  # Update the layout after removal
            self.english_radio_button_layout[i].update()  # Update the layout after removal

    def display_question(self):
        # Clear previous answers and labels
        self.french_correct_answer_label.clear()
        self.english_correct_answer_label.clear()
        self.submit_button.setEnabled(True)
        self.next_button.setEnabled(False)

        # Update the progress label to show the current number of answered questions
        self.progress_label.setText(f"Répondues - Answered: {self.current_question_index}/{self.total_questions}")

        question_data = self.questions[self.current_question_index]
        french_question_text = question_data['question_id'] + " : \n" + question_data['french_question']
        french_answers = question_data['french_answers']

        english_question_text = question_data['question_id'] + " : \n" + question_data['english_question']
        english_answers = question_data['english_answers']

        self.remove_radio_buttons()

        # Shuffle answers
        indices = list(range(len(french_answers)))
        random.shuffle(indices)

        # Set question text
        self.french_question_label.setText(french_question_text)
        self.english_question_label.setText(english_question_text)

        self.french_correct_answer_label.setWordWrap(True) 
        self.english_correct_answer_label.setWordWrap(True) 

        self.french_question_label.setWordWrap(True) 
        self.english_question_label.setWordWrap(True) 

        self.french_question_label.setTextInteractionFlags(Qt.TextInteractionFlag(True))
        self.english_question_label.setTextInteractionFlags(Qt.TextInteractionFlag(True))

        # Create radio buttons for answers
        self.button_group = QButtonGroup()
        for i, index in enumerate(indices):  
            french_radio_button = QRadioButton()
            self.french_radio_button_layout[i].addWidget(french_radio_button)
            self.button_group.addButton(french_radio_button, i)
            self.french_answers[i].setText(french_answers[index])           

            english_radio_button = QRadioButton()
            self.english_radio_button_layout[i].addWidget(english_radio_button)
            self.button_group.addButton(english_radio_button, i)
            self.english_answers[i].setText(english_answers[index]) 
     
        self.french_correct_answer = question_data['french_correct_answer']
        self.english_correct_answer = question_data['english_correct_answer']


    def submit_answer(self):
        # Get the selected answer from radio buttons
        selected_button = self.button_group.checkedButton()

        if selected_button is None:
            return

        selection_index = None

        if selected_button:
            for i in range(len(self.french_radio_button_layout)):
                item = self.french_radio_button_layout[i].itemAt(0)
                if item is not None:
                    widget = item.widget()
                    if widget == selected_button:
                        selection_index = i
                        break

            if selection_index is None:
                for i in range(len(self.english_radio_button_layout)):
                    item = self.english_radio_button_layout[i].itemAt(0)
                    if item is not None:
                        widget = item.widget()
                        if widget == selected_button:
                            selection_index = i

        # Show correct answer and disable submit button
        if selection_index is not None:
            if self.french_answers[selection_index].text() == self.french_correct_answer or self.english_answers[selection_index].text() == self.english_correct_answer:
                self.score += 1
                self.french_correct_answer_label.setText(f"Exacte! La réponse était: {self.french_correct_answer}")
                self.french_correct_answer_label.setStyleSheet("color: green;")  # Set text color to green for correct
                self.english_correct_answer_label.setText(f"Correct! The answer was: {self.english_correct_answer}")
                self.english_correct_answer_label.setStyleSheet("color: green;")  # Set text color to green for correct
            else:
                self.french_correct_answer_label.setText(f"Erreur! La réponse était: {self.french_correct_answer}")
                self.french_correct_answer_label.setStyleSheet("color: red;")  # Set text color to red for incorrect
                self.english_correct_answer_label.setText(f"Incorrect! The correct answer was: {self.english_correct_answer}")
                self.english_correct_answer_label.setStyleSheet("color: red;")  # Set text color to red for incorrect

        self.submit_button.setEnabled(False)
        self.next_button.setEnabled(True)

    def next_question(self):
        self.current_question_index += 1
        if self.current_question_index >= self.total_questions:
            self.show_score()
        else:
            self.display_question()

    def show_score(self):
        percentage = (self.score / self.total_questions) * 100
        result = "Vous avez Réussi! / You Passed!" if percentage >= 70 else "Vous avez Échoué... / You Failed..."
        self.score_label.setStyleSheet("color: green;") if percentage >= 70 else self.score_label.setStyleSheet("color: red;")
        self.score_label.setText(f"Your score: {self.score}/{self.total_questions} ({percentage:.2f}%)\n{result}")

        # Disable buttons after score is shown
        self.submit_button.setEnabled(False)
        self.next_button.setEnabled(False)

    def update_time(self):
        # Get elapsed time in milliseconds from the QElapsedTimer
        elapsed_time = self.elapsed_timer.elapsed()  # Time in milliseconds
        seconds = elapsed_time // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        formatted_time = f"{minutes:02}:{seconds:02}"  # Format time as MM:SS

        # Update the elapsed time label
        self.elapsed_time_label.setText(f"Chronomètre / Time: {formatted_time}")


def process_text_file(input_file, total_questions, all_sections):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        return []

    # Prepare a list to hold all questions and answers
    questions = []

    if total_questions > len(lines):
        total_questions = len(lines)

    # Read all lines and store questions with their answers
    for line in lines:
        # Split each line into parts based on the ';' delimiter
        parts = line.strip().split(';')

        if len(parts) < 11:  # Ensuring we have all necessary parts (11 expected)
            # If the line doesn't have enough parts (question and answers), skip it
            continue

         # Extract question data
        question_id = parts[0].strip()
        english_question = parts[1].strip()
        english_answers = [parts[i].strip() for i in range(2, 6)]
        french_question = parts[6].strip()
        french_answers = [parts[i].strip() for i in range(7, 11)]

        # Prepare the question data
        question_data = {
            'question_id': question_id,
            'question_section': question_id[2:5],
            'french_question': french_question,
            'french_correct_answer': french_answers[0],
            'french_answers': french_answers,
            'english_question': english_question,
            'english_correct_answer': english_answers[0],
            'english_answers': english_answers,
        }

        # Add the question data to the list
        questions.append(question_data)

    # Shuffle the questions list for the shuffled output file
    random.shuffle(questions)

    if all_sections:    
        #-------------------------------------------------------------------------------------------------------
        # From the shuffles question, start looking them one by one and sort them based on the question category.
        # Sort them in 8 differents lists. Once all list are full get out of the loop.
        # The Full cutoff limit is based on the total questions integer.
        cutoff = math.ceil(total_questions / 8)
        selected_questions = []
        selected_question_count = {f'{i:03}': 0 for i in range(1, 9)}

        sorted_questions = []
        for i in range(len(questions)):
                question_section = questions[i]['question_section']
                if selected_question_count[question_section] < cutoff: 
                    selected_questions.append(questions[i]) 
                    selected_question_count[question_section] += 1 
        #-------------------------------------------------------------------------------------------------------- 
    else:
        selected_questions = questions


    return selected_questions

if __name__ == "__main__":
    # Set up quiz questions from file
    input_file = 'C://Users//franc//dev//jupyter//projects//ham-exams//questions_basic_2024_s3.txt'

    # From this shuffled list and a defined total number of question, extract questions from each of the sections 
    total_questions = 1000
    all_sections = True  # Put false if you just want one section (ensure that the input questions is the corrrect one... tmeporary)

    questions = process_text_file(input_file, total_questions, all_sections) # return the entire list of questions completely shuffled

    # Make sure we have loaded the questions
    if not questions:
        print("No questions loaded.")
    else:
        # Run the quiz app if questions were successfully loaded
        app = QApplication(sys.argv)
        window = QuizApp(questions)
        window.show()
        sys.exit(app.exec())
