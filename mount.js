import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.js";

// Calculate the base path for GitHub Pages or local development.
const isGitHubPages = window.location.hostname.includes('github.io');
const pathSegments = window.location.pathname.split('/');
const repoName = isGitHubPages ? pathSegments[1] : '';
const basePath = repoName ? `/${repoName}/` : '/';

fetch(basePath + "requirements.txt")
  .then((response) => {
    if (!response.ok) {
      throw new Error(`Failed to fetch requirements.txt: ${response.statusText}`);
    }
    return response.text();
  })
  .then((text) => {
    const requirements = text
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith("#") && !line.startsWith("streamlit"));

    mount(
      {
        requirements: requirements,
        entrypoint: "streamlit_app.py",
        files: {
          "streamlit_app.py": {
            url: basePath + "streamlit_app.py",
          },
          "pages/markitdown.py": {
            url: basePath + "pages/markitdown.py",
          },
          "requirements.txt": {
            url: basePath + "requirements.txt",
          },
        },
        streamlitConfig: {
          "server.baseUrlPath": basePath,
        },
      },
      document.getElementById("root")
    );
  })
  .catch((error) => {
    console.error("Error loading requirements:", error);
    // Display a user-friendly error message if requirements fail to load
    document.getElementById("root").innerHTML = `
      <div style="padding: 20px; color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; font-family: sans-serif;">
        <h2>Initialization Error</h2>
        <p>Could not load <code>requirements.txt</code>. Please ensure the file exists and is accessible.</p>
        <pre>${error.message}</pre>
      </div>
    `;
  });
