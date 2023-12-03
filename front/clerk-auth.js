const publishableKey =
  "pk_test_bm92ZWwtcGFyYWtlZXQtMzIuY2xlcmsuYWNjb3VudHMuZGV2JA";

let globalUserId = null;
let globalUserName = null;

const startClerk = async () => {
  const Clerk = window.Clerk;

  try {
    // Charger l'environnement et la session Clerk si disponible
    await Clerk.load({
      afterSignInUrl: "/quiz.html",
      afterSignUpUrl: "/quiz.html",
    });

    const userButton = document.getElementById("user-button");

    Clerk.addListener(({ user }) => {
      if (user) {
        // Récupération des informations de l'utilisateur s'il est connecté
        globalUserId = user.id;
        globalUserName = user.username;

        // Bouton utilisateur avec l'ID utilisateur s'il existe
        if (userButton) {
          Clerk.mountUserButton(userButton, {
            appearance: {
              elements: {
                userButtonTrigger: { marginRight: 10 },
                avatarBox: { width: 50, height: 50 },
              },
            },
            afterSignOutUrl: "/",
          });
        }
      }
    });
  } catch (err) {
    console.error("Erreur lors du démarrage de Clerk : ", err);
  }
};

(() => {
  const script = document.createElement("script");
  script.setAttribute("data-clerk-publishable-key", publishableKey);
  script.async = true;
  script.src = `https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js`;
  script.crossOrigin = "anonymous";
  script.addEventListener("load", startClerk);
  script.addEventListener("error", () => {
    console.error("Erreur lors du chargement du script Clerk.");
  });
  document.body.appendChild(script);
})();
