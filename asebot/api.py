from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import asebot.config

sample_transport=RequestsHTTPTransport(
    url=asebot.config.GRAPHQL_ENDPOINT,
    verify=False,
    retries=3,
)

client = Client(
    transport=sample_transport,
    fetch_schema_from_transport=True,
)


def load_books():
    query = gql('''
        {
        books(sort: "title") {
            id
            title
            cover {
            url
            }
        }
        }
    ''')
    return client.execute(query)["books"]

def load_book(book_id):
    query = gql('''
{
  book(id: %s) {
    title
    pages {
      text
      images {
        url
      }
    }
    quizz {
      questions {
        question
        image {url}
        answer
        distractors {
          wrong_answer
        }
      }
    }
  }
}
    ''' % book_id)
    return client.execute(query)["book"]

def load_level_Selection():
    query = gql('''
        {
          levelSelectionPictures {
            id
            Image {url}
          }
        }
    ''')
    return client.execute(query)['levelSelectionPictures']

def load_books_on_level(book_level_id):
    query = gql('''
      {
        books(sort: "title", where: { level: {id: %s}  }) {
            id
            title
    level {name id}
            cover {
            url
            }

        }
        }
    ''' % book_level_id)
    return client.execute(query)["books"]











