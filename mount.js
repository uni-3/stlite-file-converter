import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.js";

// Calculate the base path for GitHub Pages or local development.
const isGitHubPages = window.location.hostname.includes('github.io');
const pathSegments = window.location.pathname.split('/');
const repoName = isGitHubPages ? pathSegments[1] : '';
const basePath = repoName ? `/${repoName}/` : '/';

mount(
  {
    requirements: ["markitdown-no-magika", "pdfminer.six", "pypdf", "tabulate"],
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
