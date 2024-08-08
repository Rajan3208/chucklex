import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.3/firebase-app.js";
        import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.12.3/firebase-auth.js";
        import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.12.3/firebase-analytics.js";

        const firebaseConfig = {
            apiKey: "AIzaSyCiOeOL1UlS3R1_Fh7ZVYavSN1hSJTJvUo",
            authDomain: "chucklex-login.firebaseapp.com",
            projectId: "chucklex-login",
            storageBucket: "chucklex-login.appspot.com",
            messagingSenderId: "281898734329",
            appId: "1:281898734329:web:b6c81357de72a7020b8828",
            measurementId: "G-2GHHY4VDHQ"
          };

        // Initialize Firebase
        const app = initializeApp(firebaseConfig);
        const analytics = getAnalytics(app);
        const auth = getAuth();
        auth.languageCode = 'en';

        const provider = new GoogleAuthProvider();

        document.getElementById("google-login-btn").addEventListener("click", function() {
            signInWithPopup(auth, provider)
                .then((result) => {
                    console.log("Login successful:", result);
                    const credential = GoogleAuthProvider.credentialFromResult(result);
                    const user = result.user;
                    console.log("User:", user);
                    window.location.href = "/";
                })
                .catch((error) => {
                    const errorCode = error.code;
                    const errorMessage = error.message;
                    const email = error.customData.email;
                    const credential = GoogleAuthProvider.credentialFromError(error);
                    console.error(`Error [${errorCode}]: ${errorMessage}, Email: ${email}, Credential: ${credential}`);
                });
        });