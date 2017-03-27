import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Question

class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

# helper function to create question with custom time offset
def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200) # check that response is sent
        self.assertContains(response, "No polls are available") # empty set text s present in view
        self.assertQuerysetEqual(response.context['latest_questions_list'], []) # check that set is indeed empty

    def test_index_view_with_a_past_question(self):
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions_list'],
            ['<Question: Past question>']
        )

    def test_index_view_with_a_future_question(self):
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions_list'],
            []
        )

    def test_index_view_with_a_future_and_past_question(self):
        create_question(question_text="Future question", days=30)
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions_list'],
            ['<Question: Past question>']
        )

    def test_index_view_with_multiple_past_questions(self):
        create_question(question_text="Past question1", days=-30)
        create_question(question_text="Past question2", days=-2)
        response = self.client.get(reverse('polls:index'))
        # Test that they are both there and sorted by time
        self.assertQuerysetEqual(
            response.context['latest_questions_list'],
            ['<Question: Past question2>', '<Question: Past question1>']
        )
