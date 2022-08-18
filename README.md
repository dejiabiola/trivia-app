# Getting Started

### Backend Dependencies

- Python 3.10 (comes with pip), Install [Here](https://www.python.org/downloads/)
- Setup virtual environment. Navigate to the backend directory in your terminal.
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- Pip Dependencies, run `pip install -r requirements.txt` in your terminal
- Database Setup
  ```
  dropdb trivia
  createdb trivia
  psql trivia < trivia.psql
  ```
- Go to backend folder and open your terminal and run the following
  ```bash
  export FLASK_APP=flaskr
  export FLASK_DEBUG=True
  flask run
  ```

### Frontend Dependencies

Open a separate terminal, navigate to the frontend directory and run the following

- Ensure you have node installed `node -v`. If you don't follow the next step, else skip to the 3rd one.
- Install Node and NPM from [https://nodejs.com/en/download](https://nodejs.org/en/download/).
- Run `npm install` in your terminal.
- Run `npm start`

# Testing

To run the tests, open your terminal and run

```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python3 test_flaskr.py
```

# API Reference

## Getting Started

- Base URL: This app is locally hosted at `http://127.0.0.1:5000/`.
- Authentication: This version of the application does not require authentication or API keys.

## Error Handling

Errors are returned as JSON objects in the following format:

- Sample: curl http://127.0.0.1:5000/nonsense

```
{
  "success": False,
  "error": 422,
  "message": "unprocessable entity"
}
```

The API will return four error types when requests fail:

- 400: Bad Request
- 404: Resource Not Found
- 405: Method not allowed
- 422: Not Processable

## Endpoints

### GET /questions

- **General**:
  - Returns lists of question objects and categories, success value, and total number of questions
  - Results are paginated in groups of 10, include a request argument to choose page number, starting from 1 (Which is also a default value)
- **Sample**: `curl http://127.0.0.1:5000/questions`
  <br>
  ```
  {
      "success": True,
      "questions" : [
          {
              "question": "What year did the first world war end",
              "answer": "1918",
              "category": "History",
              "difficulty": 3
          },
          {
              "question": "Obama was the ___ president of the United States",
              "answer": "44th",
              "category": "History",
              "difficulty": 3
          },  .....
      ],
      "categories": {
          "Science": 1,
          "Art": 5,
          "Geography": 2,
          "History": 1,
          "Entertainment": 9,
          "Sports": 5
        },
      "total_questions": 10
  }
  ```

### POST /questions

- **General**:
  - Creates a new question using the submitted question value, answer, difficulty, and category.
  - Returns success value, questions list paginated based on the page number, the inserted question, and total number of questions
- **Sample**: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question":"Best city in the UK?", "answer":"Glasgow", "difficulty":1, "category":1}'`

```
  {
    "success": True,
    "questions" : [
            {
                "question": "Best city in the UK?",
                "answer": "Glasgow",
                "category": 1,
                "difficulty": 1
            },
            {
                "question": "What year did the first world war end",
                "answer": "1918",
                "category": "History",
                "difficulty": 3
            },
            {
                "question": "Obama was the ___ president of the United States",
                "answer": "44th",
                "category": "History",
                "difficulty": 3
            },  .....
        ],
    "new_question": {
            "question": "Best city in the UK?",
            "answer": "Glasgow",
            "category": 1,
            "difficulty": 1
        },
    "total_questions": 11
  }
```

### DELETE /questions

- **General**:
  - Deleted the question with the given ID if exists
  - Returns success value and the deleted question id
- **Sample**: `curl -X DELETE http://127.0.0.1:5000/questions/2`

```
    {
        "success": True,
        "deleted": 2,
    }
```

### POST /questions/search

- **General**:
  - search for questions that contain the given search term
  - Returns success value, number of total questions,current category, and questions list that contains the given search term.
- **Sample**: `curl http://127.0.0.1:5000/questions/search -X POST -H "Content-Type: application/json" -d '{"searchTerm":"Obama"}'`

```
    {
        "success":True,
        "questions":[
            {
                "question": "Obama was the ___ president of the United States",
                "answer": "44th",
                "category": "History",
                "difficulty": 3
            }
        ],
        "total_questions": 1
    }
```

### GET /categories/1/questions

- **General**: - Gets list of questions based on the submitted category. - Returns success value, total number of questions, current category, and list of the retrieved questions within this category - The questions are paginated based on the current page number
- **Sample**: `curl http://127.0.0.1:5000/categories/4/questions`

```
    {
        "success": True,
        "questions":[
            {
                "question": "What was the first animated Disney film?",
                "answer": "Snow White and the Seven Dwarfs",
                "category": "Entertainment",
                "difficulty": 2
            },
            {
                "question": "What is the name of Billie Eilish's debut album?",
                "answer": "When We All Fall Asleep, Where Do We Go?",
                "category": "Entertainment",
                "difficulty": 4
            }
        ],
        "total_questions": 2,
        "current_category": "Entertainment"
    }
```

### GET /quizzes

- **General**:
  - Returns a random question within the submitted category which is not in the submitted list of previous questions
- **Sample**: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"quiz_category":"Entertainment", "previous_questions":[]}'`

```
    {
        "success": True,
        "question":{
            "question": "Who plays Tommy Shelby in Peaky Blinders?",
            "answer": "Cillian Murphy",
            "category": "Entertainment",
            "difficulty": 2
        }
    }
```

### GET /categories

- **General**:
  - Returns a categories object, success value, and total number of categories
- **Sample**: `curl http://127.0.0.1:5000/categories`

```
    {
        "success": True,
        "categories": {
          "Science": 1,
          "Art": 5,
          "Geography": 2,
          "History": 1,
          "Entertainment": 9,
          "Sports": 5
        },
        total_categories: 23
    }
```

### POST /categories

- **General**:
  - Creates a new category using the submitted category type.
  - Returns success value and the new category object.
- **Sample**: `curl http://127.0.0.1:5000/categories -X POST -H "Content-Type: application/json" -d '{"type": "Technology"}'`

```
  {
    "success": True,
    "category": {
        "id": 5,
        "type": "Technology"
    }
  }
```
