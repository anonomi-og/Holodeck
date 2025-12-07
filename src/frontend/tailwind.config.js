/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'holodeck-dark': '#0f172a',
                'holodeck-accent': '#38bdf8',
                'holodeck-panel': '#1e293b',
            },
        },
    },
    plugins: [],
}
