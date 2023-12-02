document.getElementById("navbar").innerHTML =
  '<object type="text/html" data="navbar.html"></object>';

// Récupérer les meilleurs scores depuis le backend et les afficher
function fetchQuizInfos() {
  fetch("http://localhost:8000/quiz_infos")
    .then((response) => response.json())
    .then((data) => {
      const scoreList = document.getElementById("score-list");

      data.scores.forEach((score) => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${score.username}</td><td>${score.score}</td>`;
        scoreList.appendChild(row);
      });

      $("#loader").addClass("hide");
      $("#content").removeClass("hide");

      clearInterval(loadingInterval);
    })
    .catch(() => {
      console.log("Le back-end ne répond pas.");
    });
}

fetchQuizInfos();
const loadingInterval = setInterval(fetchQuizInfos, 10000);

const startQuizButton = document.getElementById("start-quiz-button");
startQuizButton.addEventListener("click", async () => {
  const user = window.Clerk.user;
  if (user) {
    window.location.href = "quiz.html";
  } else {
    window.location.href = "clerk-auth.html";
  }
});
