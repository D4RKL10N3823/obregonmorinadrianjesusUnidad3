import { gsap } from "https://cdn.skypack.dev/gsap";

window.addEventListener('load', () => {
    // Selecciona todas las cards con la clase .glide para mostrarlas de 5.5 en 5.5 en el carrusel
    document.querySelectorAll('.glide').forEach(glideEl => {
        const glide = new Glide(glideEl, {
            type: 'carousel',
            perView: 5.5,
            gap: 20,
            breakpoints: {
                1792: { perView: 5.5 },
                1536: { perView: 5 },
                1280: { perView: 4 },
                1024: { perView: 3 },
                768:  { perView: 2 },
                480:  { perView: 1 },
            },
        });

        glide.mount();
    });
    
    // Seleccionar un anime aleatorio al hacer doble click en el titulo de la categoria
    document.querySelectorAll('.category-title').forEach((categoryTitle, index) => {
        categoryTitle.addEventListener('dblclick', () => {
            const categoriesData = JSON.parse(document.getElementById('categories-data').textContent);
            const key = `animes-${index + 1}`;
            const animes = categoriesData[key];
            if (!animes || !animes.length) return;

            const randomAnime = animes[Math.floor(Math.random() * animes.length)];
            window.location.href = `/anime/${encodeURIComponent(randomAnime.title)}`;
        });
    });

    // Botón para seleccionar un anime aleatorio
    const btn = document.getElementById("surprise-btn");
    const img = document.getElementById("anime-img");
    const viewBtn = document.getElementById("view-anime-btn");
    const animeTitle = document.getElementById("view-anime-title");
    const animeQuestion = document.getElementById("view-anime-question");

    const categoriesData = JSON.parse(document.getElementById('categories-data').textContent);
    const allAnimes = Object.values(categoriesData).flat();

    btn.addEventListener("click", () => {
        let totalFrames = 20;
        let interval = 0.05;

        const tl = gsap.timeline();
        
        tl.to({}, {
            duration: totalFrames * interval,
            // Muestra la animación de las imagenes y el titulo de los animes de forma aleatoria
            onUpdate: () => {
                const randomAnime = allAnimes[Math.floor(Math.random() * allAnimes.length)];
                img.src = randomAnime.image;
                img.classList.remove("hidden");

                animeTitle.textContent =  randomAnime.title;
                animeTitle.classList.remove("hidden");

                gsap.fromTo(img, { opacity: 0.1, scale: 1.1 }, { opacity: 0.2, scale: 1, duration: 0.08 });
            },
            // Muestra el anime que se escogio aleatoriamente con su titulo e imagen
            onComplete: () => {
                const finalAnime = allAnimes[Math.floor(Math.random() * allAnimes.length)];
                animeQuestion.classList.add("hidden");
                
                animeTitle.textContent = finalAnime.title;
                gsap.fromTo(animeTitle, { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.3 });
                animeTitle.classList.remove("hidden");
                
                img.src = finalAnime.image;
                img.classList.remove("hidden");

                viewBtn.classList.remove("hidden");
                viewBtn.href = finalAnime.url;
            }
        });
    });
});