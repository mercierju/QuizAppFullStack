let currentQuestion = 0;
let userAnswers = [];

// Fonction pour afficher la question actuelle
function displayQuestion(questionData) {
  const questionContainer = document.getElementById("question-container");
  const questionText = questionData[0]["question_text"];

  questionContainer.textContent = questionText;

  const choicesList = document.getElementById("choices-list");
  choicesList.innerHTML = "";

  questionData[1].forEach((choice) => {
    const choiceItem = document.createElement("ul");
    choiceItem.innerHTML = `<label><input type="radio" name="choice" value="${choice.id}">${choice.choice_text}</label>`;
    choicesList.appendChild(choiceItem);
  });
}

// Charger le nombre total de questions depuis le backend
let totalQuestions;

fetch("http://localhost:8000/quiz_infos")
  .then((response) => response.json())
  .then((data) => {
    totalQuestions = data.size;

    // Charger la première question depuis le backend
    fetch(`http://localhost:8000/questions/${currentQuestion}`)
      .then((response) => response.json())
      .then((data) => {
        displayQuestion(data);
      });
  });

// Gérer le clic sur le bouton "Valider mes réponses"
const submitButton = document.getElementById("submit-button");
submitButton.addEventListener("click", () => {
  const selectedChoice = document.querySelector('input[name="choice"]:checked');
  if (selectedChoice) {
    userAnswers.push(parseInt(selectedChoice.value));
    currentQuestion++;
    if (currentQuestion < totalQuestions) {
      // Charger la question suivante depuis le backend
      fetch(`http://localhost:8000/questions/${currentQuestion}`)
        .then((response) => response.json())
        .then((data) => {
          displayQuestion(data);
        });
    } else {
      // Envoyer les réponses au backend et rediriger vers la page des résultats
      fetch("http://localhost:8000/participation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          answers: userAnswers,
          username: globalUserName,
          clerkId: globalUserId,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Rediriger vers la page des résultats avec les données
          window.location.href = `results.html?score=${data.score}`;
        });
    }
  }
});
