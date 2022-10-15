/* eslint-disable semi */
/* eslint-disable comma-dangle */
/* eslint-disable quotes */
/** @type {import('tailwindcss').Config} */

module.exports = {
  content: ["./templates/**/*.html", "./node_modules/flowbite/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [require("flowbite/plugin")],
};
