// TZD Labs · Systems — Observable Framework configuration
export default {
  root: "src",
  base: "/Systems/",
  // Use the project venv Python so data loaders find all packages
  interpreters: {
    ".py": ["/Users/shakes/DevProjects/Systems/.venv/bin/python3"],
  },
  title: "How Capital Becomes Infrastructure",
  theme: "air",
  toc: false,
  head: `
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="./style.css">
  `,
  pages: [
    { name: "Markets & Money", path: "/dd001" },
    { name: "The Conversion Gap", path: "/dd001-conversion" },
    { name: "Who Holds the Downside", path: "/dd001-risk" },
    { name: "Grid Modernization", path: "/dd002" },
    { name: "Labor Markets", path: "/dd003" },
    { name: "Who Pays for the Grid", path: "/dd004" }
  ],
  footer: "TZD Labs · Systems Research — Technology Capital in the Physical Economy",
};
