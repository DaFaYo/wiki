from django.test import TestCase

from encyclopedia import util
from django.core.files.storage import default_storage
from markdown2 import Markdown

markdowner = Markdown()  

TEST_TITLE = "test_bakerstreet"
TEST_CONTENT = "Sherlock Holmes lives in Bakerstreet, London."


# delete function only for testing purposes
def delete_entry(title):
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)


# Create your tests here.
class EncyclopediaTestClass(TestCase):
   
    @classmethod
    def setUpClass(cls):
        super().setUpClass()      
        entries = util.list_entries()
        if TEST_TITLE not in entries:
            util.save_entry(TEST_TITLE, TEST_CONTENT)


    @classmethod
    def tearDownClass(cls):
        delete_entry(TEST_TITLE)
        super().tearDownClass()


    
    def test_index_page_shows_all_entries(self):      
        entries = util.list_entries()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)   
        self.assertEqual(response.context["entries"], entries)


    def test_entry_page_shows_content_information_of_entry(self):
        response = self.client.get('/wiki/' + TEST_TITLE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["entry"], TEST_TITLE)
        self.assertEqual(response.context["entry_content"], markdowner.convert(TEST_CONTENT))
          
        
    def test_if_page_not_exists_a_different_page_should_be_shown(self):
        response = self.client.get('/wiki/' + TEST_TITLE + TEST_TITLE)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "encyclopedia/pageNotFound.html")


    def test_search_with_exact_match_returns_the_page_for_entry(self):
        response = self.client.get('/search_results?q=' + TEST_TITLE, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "encyclopedia/entry.html")
        self.assertEqual(response.context["entry"], TEST_TITLE)
    
    def test_search_with_substring_match_returns_titles_containing_substrings(self):

        substring = TEST_TITLE[:len(TEST_TITLE) - 1]
        matching_results = list(filter(lambda title: substring in title, util.list_entries()))
        response = self.client.get('/search_results?q=' + substring, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "encyclopedia/search_results.html")
        self.assertEqual(matching_results, response.context["search_results"])

    def test_create_page_for_new_title_adds_the_page_to_all_pages(self):
        # to implement
        pass

    def test_create_page_for_existing_title_shows_error_message_page_not_created(self):
        # to implement
        pass

    def test_edit_page_successfully_edits_and_saves_new_page_content(self):
        # to implement
        pass


    def test_random_page_redirects_to_a_random_entry(self):  
        entries = util.list_entries()
        response = self.client.get('/random_page', follow=True)
        title = response.context["entry"]
        url = "/wiki/" + title

        self.assertRedirects(response, url,  status_code=302, 
          target_status_code=200, fetch_redirect_response=True) 
            
        self.assertTemplateUsed(response, "encyclopedia/entry.html")
        self.assertTrue(title in entries)
