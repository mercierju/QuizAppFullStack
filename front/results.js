const resultMessage = document.getElementById('result-message');
const score = document.getElementById('score');

// Récupérer le score depuis les paramètres de l'URL
const searchParams = new URLSearchParams(window.location.search);
const scoreValue = searchParams.get('score');

fetch("http://localhost:8000/quiz_infos")
  .then(response => response.json())
  .then(data => {
    quizSize = data.size;
    console.log(quizSize);

    // Mettez le code qui dépend de quizSize ici
    console.log('scorevalue', scoreValue);
    if (scoreValue) {
      if (scoreValue * 100 / quizSize >= 0.8) {
        resultMessage.textContent = 'Félicitations, vous avez réussi le quiz !';
      } else {
        resultMessage.textContent = 'Dommage, vous n\'avez pas réussi le quiz.';
      }
      score.textContent = `Score : ${scoreValue}/${quizSize}`;
    } else {
      resultMessage.textContent = 'Aucun résultat disponible.';
    }
  })
  .catch(error => {
    console.error('Erreur lors de la récupération des données:', error);
  });

// Rediriger vers la page d'accueil lorsque le bouton est cliqué
const backToHomeButton = document.getElementById('back-to-home-button');
backToHomeButton.addEventListener('click', () => {
  window.location.href = 'index.html';
});