/** @type {import("tailwindcss").Config} */
const {InjectManifest} = require("workbox-webpack-plugin");

module.exports = {
    content: [
        "./templates/**/*.html",
        "./node_modules/flowbite/**/*.js"
    ],
    darkMode: "class",
    theme: {
        extend: {}
    },
    plugins: [
        require("flowbite/plugin"),
        require('flowbite-typography'),
        new InjectManifest({
            swSrc: "./static/js/sw.js"
        })
    ]
};
