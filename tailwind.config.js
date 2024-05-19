/** @type {import('tailwindcss').Config} */
module.exports = {

    content: ["./src/**/*.{html,js}",
        './templates/**/*.html',
      './node_modules/flowbite/**/*.js'],
    theme: {
        extend: {},
    },
    plugins: ["tailwindcss ,autoprefixer",
        require('flowbite/plugin')
    ],


}

