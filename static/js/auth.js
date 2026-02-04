function togglePassword(inputId, iconId) {

    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);

    if (!input || !icon) {
        console.log("Toggle Error: Element not found");
        return;
    }

    // Show icon
    const eye = `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
         fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-width="2"
        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
      <path stroke-width="2"
        d="M2.458 12C3.732 7.943 7.523 5 
           12 5c4.478 0 8.268 2.943 
           9.542 7-1.274 4.057-5.064 
           7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
    </svg>
    `;

    // Hide icon
    const eyeSlash = `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
         fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-width="2" d="M3 3l18 18"/>
      <path stroke-width="2"
        d="M10.585 10.585a2 2 0 002.83 2.83"/>
      <path stroke-width="2"
        d="M16.681 16.681A8.96 8.96 0 0112 18
           c-4.418 0-8.208-2.946-9.455-7
           a9.99 9.99 0 012.396-3.775"/>
      <path stroke-width="2"
        d="M6.318 6.318A8.96 8.96 0 0112 6
           c4.418 0 8.208 2.946 9.455 7
           a9.99 9.99 0 01-4.421 5.318"/>
    </svg>
    `;


    if (input.type === "password") {

        input.type = "text";
        icon.innerHTML = eyeSlash;

    } else {

        input.type = "password";
        icon.innerHTML = eye;

    }
}
