from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import asebot.config

sample_transport = RequestsHTTPTransport(
    url=asebot.config.GRAPHQL_ENDPOINT,
    verify=False,
    retries=3,
)

client = Client(
    transport=sample_transport,
    fetch_schema_from_transport=True,
)


class ConnectAPI:

    def createPoints(self, chatID, userName, points):
        query = gql(
            """ mutation {
              createPoint(
                input: { data: {chatId:"%s", username:"%s", totalPoints:%d } }) 
              {
                point {
                  chatId
                  username
                  totalPoints
                }
              }
            } """ % (chatID, userName, points)
        )
        client.execute(query)

    def updatePoints(self, id, points):
        query = gql(
            """ mutation {
              updatePoint(
                input: {
                  where: { id: "%s" }
                  data: { totalPoints:%d }
                }
              ) {
                point {
                  totalPoints
                }
              }
            } """ % (id, points)
        )
        client.execute(query)

    def getPoints(self, chatId):
        query = gql(
            """ query {
              points(where: {chatId: "%s"}) {
                id
                chatId
                username
                totalPoints
              }
            } """ % chatId
        )
        return client.execute(query)

    def get_top10(self):
        query = gql(
            """ query {
          points(limit:10 ,sort: "totalPoints:desc") {
            chatId
            username
            totalPoints
          }
        } """
        )
        return client.execute(query)

    def load_lesson(self, grade, unit, lesson):
        query = gql(
            """ {
                  lessonContents(where: {grade: "%s" unit: "%s" lesson: "%s"}){
                    id
                    recordings{url}
                    page{images{url} text audio{url} video}
                    lesson_quizz{instructions questions {
                      question
                      image {url}
                      answer
                      distractors {
                        wrong_answer
                        }
                        audio{url}
                        video
                      }
                    }
                  }
                } """ % (grade, unit, lesson)
        )
        return client.execute(query)["lessonContents"]
      
    def load_unit_quiz(self, grade, unit):
      query = gql(
        """
        {
          unitQuizs(where:{Grade:"%s" Unit:"%s"}){
            id
            Instructions
            Questions{
              question
              image {url}
              answer
              distractors{
                wrong_answer
                }
              audio{url}
              video
              }
            }
          }""" % (grade, unit)
        )
      return client.execute(query)["unitQuizs"]
    
    def load_unit_quiz_length(self, grade):
      query = gql(
       """ 
        {
          unitQuizs(where:{Grade:"%s"}){
            Unit
            }
          } """ % (grade)
        )
      return client.execute(query)

    def load_lesson_length(self,grade,unit):
      query = gql(
       """ 
        {
         lessonContents(where:{grade:"%s" unit: "%s"}){
            id
            }
          } """ % (grade,unit)
        )
      return client.execute(query)