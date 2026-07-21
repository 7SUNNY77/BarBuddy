import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/cocktails";

function getCocktailEmoji(glass = "") {
  const normalizedGlass = glass.toLowerCase();

  if (
    normalizedGlass.includes("champagne") ||
    normalizedGlass.includes("flute")
  ) {
    return "🥂";
  }

  if (
    normalizedGlass.includes("martini") ||
    normalizedGlass.includes("cocktail") ||
    normalizedGlass.includes("nick")
  ) {
    return "🍸";
  }

  if (
    normalizedGlass.includes("highball") ||
    normalizedGlass.includes("collins")
  ) {
    return "🥃";
  }

  if (normalizedGlass.includes("mug")) {
    return "🍺";
  }

  return "🍹";
}

function getCocktailCover(tasteTags = []) {
  const tags = tasteTags.join(" ").toLowerCase();

  if (tags.includes("кофейн")) {
    return "cover-coffee";
  }

  if (tags.includes("шоколад")) {
    return "cover-chocolate";
  }

  if (tags.includes("мятн")) {
    return "cover-mint";
  }

  if (tags.includes("ягод") || tags.includes("малин") || tags.includes("вишн")) {
    return "cover-berry";
  }

  if (tags.includes("цветочн") || tags.includes("фиалков")) {
    return "cover-floral";
  }

  if (tags.includes("ананас") || tags.includes("кокос") || tags.includes("тропическ")) {
    return "cover-tropical";
  }

  if (tags.includes("персик") || tags.includes("абрикос")) {
    return "cover-peach";
  }

  if (tags.includes("текиль") || tags.includes("агав")) {
    return "cover-tequila";
  }

  if (tags.includes("ромов")) {
    return "cover-rum";
  }

  if (tags.includes("джинов")) {
    return "cover-gin";
  }

  if (tags.includes("виски") || tags.includes("бурбонов")) {
    return "cover-whiskey";
  }

  if (tags.includes("коньяч")) {
    return "cover-cognac";
  }

  if (tags.includes("игрист") || tags.includes("винн")) {
    return "cover-sparkling";
  }

  if (
    tags.includes("лимон") ||
    tags.includes("цитрус") ||
    tags.includes("лаймов") ||
    tags.includes("грейпфрут")
  ) {
    return "cover-citrus";
  }

  if (tags.includes("имбир") || tags.includes("прян") || tags.includes("остр")) {
    return "cover-spice";
  }

  if (tags.includes("сливочн") || tags.includes("десертн")) {
    return "cover-cream";
  }

  if (tags.includes("горьк") || tags.includes("травян")) {
    return "cover-herbal";
  }

  return "cover-classic";
}

function App() {
  const [cocktails, setCocktails] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [recommendationQuery, setRecommendationQuery] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationVisible, setRecommendationVisible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("Все");
  const [selectedTaste, setSelectedTaste] = useState("Все");
  const [categoriesOpen, setCategoriesOpen] = useState(false);
  const [tastesOpen, setTastesOpen] = useState(false);
  const [selectedCocktail, setSelectedCocktail] = useState(null);

  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadCatalog() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error(`Ошибка API: ${response.status}`);
        }

        const responseData = await response.json();

        // Работает и если API вернул массив, и если вернул { cocktails: [...] }.
        const catalog = Array.isArray(responseData)
          ? responseData
          : Array.isArray(responseData.items)
            ? responseData.items
            : [];

        setCocktails(catalog);
      } catch (requestError) {
        console.error(requestError);
        setError("Не удалось загрузить каталог. Запусти backend на порту 8000.");
      } finally {
        setLoading(false);
      }
    }

    loadCatalog();
  }, []);

  const categories = useMemo(() => {
    return [
      "Все",
      ...new Set(
        cocktails
          .map((cocktail) => cocktail.iba_category)
          .filter(Boolean)
          .sort()
      ),
    ];
  }, [cocktails]);

  const tasteTags = useMemo(() => {
    return [
      "Все",
      ...new Set(
        cocktails
          .flatMap((cocktail) => cocktail.taste_tags || [])
          .filter(Boolean)
          .sort()
      ),
    ];
  }, [cocktails]);

  const filteredCocktails = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return cocktails.filter((cocktail) => {
      const matchesSearch =
        !query ||
        cocktail.name_en?.toLowerCase().includes(query) ||
        cocktail.name_ru?.toLowerCase().includes(query);

      const matchesCategory =
        selectedCategory === "Все" ||
        cocktail.iba_category === selectedCategory;

      const matchesTaste =
        selectedTaste === "Все" ||
        cocktail.taste_tags?.includes(selectedTaste);

      return matchesSearch && matchesCategory && matchesTaste;
    });
  }, [cocktails, searchQuery, selectedCategory, selectedTaste]);

  async function openCocktail(cocktailId) {
    try {
      setDetailsLoading(true);

      const response = await fetch(`${API_URL}/${cocktailId}`);

      if (!response.ok) {
        throw new Error(`Ошибка загрузки рецепта: ${response.status}`);
      }

      const cocktail = await response.json();
      setSelectedCocktail(cocktail);
    } catch (requestError) {
      console.error(requestError);
      setError("Не удалось загрузить рецепт.");
    } finally {
      setDetailsLoading(false);
    }
  }

  function getRecommendations() {
    function normalizeWord(word) {
      return word
        .toLowerCase()
        .replace(/ё/g, "е")
        .replace(/[,.!?"'«»()]/g, "")
        .replace(
          /(иями|ями|ами|иями|ыми|ими|ого|ему|ому|ыми|ими|ий|ый|ой|ая|яя|ое|ее|ые|ие|ую|юю|ом|ем|ам|ям|ах|ях|ов|ев|а|я|ы|и|е|у|ю)$/u,
          ""
        );
    }

    function getWords(text) {
      return text
        .toLowerCase()
        .replace(/ё/g, "е")
        .split(/\s+/)
        .map(normalizeWord)
        .filter((word) => word.length >= 3);
    }

    const queryWords = getWords(recommendationQuery);

    if (queryWords.length === 0) {
      setRecommendations([]);
      setRecommendationVisible(true);
      return;
    }

    const rankedCocktails = cocktails
      .map((cocktail) => {
        const tags = cocktail.taste_tags || [];

        const ingredients = (cocktail.ingredients || []).map((ingredient) =>
          typeof ingredient === "string" ? ingredient : ingredient.name || ""
        );

        const searchableItems = [
          cocktail.name_en || "",
          cocktail.name_ru || "",
          cocktail.iba_category || "",
          ...tags,
          ...ingredients,
        ];

        const matches = searchableItems.filter((item) => {
          const itemWords = getWords(item);

          return queryWords.some((queryWord) =>
            itemWords.some(
              (itemWord) =>
                itemWord.includes(queryWord) || queryWord.includes(itemWord)
            )
          );
        });

        const matchedTags = tags.filter((tag) => matches.includes(tag));
        const matchedIngredients = ingredients.filter((ingredient) =>
          matches.includes(ingredient)
        );

        const score =
          matchedTags.length * 5 +
          matchedIngredients.length * 3 +
          matches.length;

        return {
          ...cocktail,
          score,
          reasons: [...new Set([...matchedTags, ...matchedIngredients])].slice(
            0,
            3
          ),
        };
      })
      .filter((cocktail) => cocktail.score > 0)
      .sort((first, second) => second.score - first.score)
      .slice(0, 3);

    setRecommendations(rankedCocktails);
    setRecommendationVisible(true);
  }

  useEffect(() => {
    const telegram = window.Telegram?.WebApp;

    if (!telegram) {
      return;
    }

    telegram.ready();
    telegram.expand();
  }, []);

  return (
    <main className="app">
      <header className="hero">
        <p className="eyebrow">BARBUDDY</p>
        <h1>Каталог коктейлей</h1>
        <p className="hero-text">
          Классические коктейли с ингредиентами и инструкциями.
        </p>
      </header>

      <section className="recommendation-box">
        <div className="recommendation-heading">
          <div>
            <p className="eyebrow">ПОДБОР ПО НАСТРОЕНИЮ</p>
            <h2>Что хочется выпить?</h2>
          </div>

          <span className="recommendation-icon">✦</span>
        </div>

        <div className="recommendation-form">
          <input
            type="text"
            value={recommendationQuery}
            placeholder="Например: что-то кислое, освежающее и с джином"
            onChange={(event) => setRecommendationQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                getRecommendations();
              }
            }}
          />

          <button type="button" onClick={getRecommendations}>
            Подобрать
          </button>
        </div>

        <p className="recommendation-hint">
          Попробуй: «сладкое и кофейное», «что-то с ромом», «лёгкое с цитрусом».
        </p>

        {recommendationVisible && (
          <div className="recommendation-results">
            {recommendations.length > 0 ? (
              <>
                <p className="results-title">Подходящие коктейли</p>

                <div className="recommendation-grid">
                  {recommendations.map((cocktail) => (
                    <button
                      className="recommendation-card"
                      type="button"
                      key={cocktail.id}
                      onClick={() => openCocktail(cocktail.id)}
                    >
                      <span className="recommendation-card-name">
                        {cocktail.name_en}
                      </span>

                      <span className="recommendation-card-ru">
                        {cocktail.name_ru}
                      </span>

                      {cocktail.reasons.length > 0 && (
                        <span className="recommendation-reason">
                          Подходит: {cocktail.reasons.join(", ")}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              </>
            ) : (
              <p className="recommendation-empty">
                Не нашёл точного совпадения. Попробуй указать вкус, алкоголь или
                ингредиент: например, «ромовый», «кислый», «джин».
              </p>
            )}
          </div>
        )}
      </section>

      <section className="filters">
        <label className="search-field">
          <span>Поиск по названию</span>
          <input
            type="search"
            placeholder="Mojito, Negroni, Маргарита..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
          />
        </label>

        <div className="filter-summary">
          <button
            className={`filter-toggle ${categoriesOpen ? "is-open" : ""}`}
            type="button"
            aria-expanded={categoriesOpen}
            onClick={() => setCategoriesOpen((isOpen) => !isOpen)}
          >
            <span>Категория</span>
            <strong>{selectedCategory}</strong>
            <span className="toggle-arrow">⌄</span>
          </button>

          <button
            className={`filter-toggle ${tastesOpen ? "is-open" : ""}`}
            type="button"
            aria-expanded={tastesOpen}
            onClick={() => setTastesOpen((isOpen) => !isOpen)}
          >
            <span>Вкус</span>
            <strong>{selectedTaste}</strong>
            <span className="toggle-arrow">⌄</span>
          </button>
        </div>

        {categoriesOpen && (
          <div className="filter-panel">
            <div className="filter-panel-heading">
              <span>Выберите категорию</span>

              {selectedCategory !== "Все" && (
                <button
                  className="reset-filter"
                  type="button"
                  onClick={() => setSelectedCategory("Все")}
                >
                  Сбросить
                </button>
              )}
            </div>

            <div className="filter-chips">
              {categories.map((category) => (
                <button
                  className={`filter-chip ${
                    selectedCategory === category ? "is-active" : ""
                  }`}
                  key={category}
                  type="button"
                  onClick={() => {
                    setSelectedCategory(category);
                    setCategoriesOpen(false);
                  }}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        )}

        {tastesOpen && (
          <div className="filter-panel">
            <div className="filter-panel-heading">
              <span>Выберите вкус</span>

              {selectedTaste !== "Все" && (
                <button
                  className="reset-filter"
                  type="button"
                  onClick={() => setSelectedTaste("Все")}
                >
                  Сбросить
                </button>
              )}
            </div>

            <div className="filter-chips">
              {tasteTags.map((tag) => (
                <button
                  className={`filter-chip ${
                    selectedTaste === tag ? "is-active" : ""
                  }`}
                  key={tag}
                  type="button"
                  onClick={() => {
                    setSelectedTaste(tag);
                    setTastesOpen(false);
                  }}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="catalog-heading">
        Найдено коктейлей: <strong>{filteredCocktails.length}</strong>
      </section>

      {loading && <p className="empty-state">Загружаем каталог...</p>}

      {error && <p className="empty-state error-message">{error}</p>}

      {!loading && !error && filteredCocktails.length === 0 && (
        <p className="empty-state">
          Коктейли не найдены. Попробуй изменить поиск или фильтры.
        </p>
      )}

      {!loading && !error && filteredCocktails.length > 0 && (
        <section className="cocktail-grid">
          {filteredCocktails.map((cocktail) => (
            <article
              className="cocktail-card"
              key={cocktail.id}
              onClick={() => openCocktail(cocktail.id)}
            >
              <div
                className={`card-image ${getCocktailCover(cocktail.taste_tags)}`}
                aria-label={`Обложка коктейля ${cocktail.name_en}`}
              >
                <span className="card-glass-icon">
                  {getCocktailEmoji(cocktail.glass)}
                </span>

                <span className="card-image-glow" />
              </div>

              <div className="card-content">
                <p className="category">{cocktail.iba_category}</p>
                <h2>{cocktail.name_en}</h2>
                <p className="name-ru">{cocktail.name_ru}</p>

                <div className="tags">
                  {(cocktail.taste_tags || []).slice(0, 3).map((tag) => (
                    <span className="tag" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </section>
      )}

      {detailsLoading && (
        <div className="details-loading">Загружаем рецепт...</div>
      )}

      {selectedCocktail && (
        <div
          className="modal-backdrop"
          onClick={() => setSelectedCocktail(null)}
        >
          <section
            className="cocktail-modal"
            role="dialog"
            aria-modal="true"
            aria-label={`Рецепт: ${selectedCocktail.name_en}`}
            onClick={(event) => event.stopPropagation()}
          >
            <button
              className="modal-close"
              type="button"
              onClick={() => setSelectedCocktail(null)}
              aria-label="Закрыть"
            >
              ×
            </button>

            <div className="modal-hero">
              <div className="modal-image-placeholder">
                {selectedCocktail.image_url ? (
                  <img
                    src={selectedCocktail.image_url}
                    alt={selectedCocktail.name_en}
                  />
                ) : (
                  "🍸"
                )}
              </div>

              <div>
                <p className="category">{selectedCocktail.iba_category}</p>
                <h2 className="modal-title">{selectedCocktail.name_en}</h2>
                <p className="modal-name-ru">{selectedCocktail.name_ru}</p>

                <div className="modal-tags">
                  {(selectedCocktail.taste_tags || []).map((tag) => (
                    <span className="tag" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <p className="modal-description">
              {selectedCocktail.taste_description_ru}
            </p>

            <div className="recipe-meta">
              <div className="meta-item">
                <span className="meta-label">Крепость</span>
                <strong>{selectedCocktail.abv_estimate ?? "—"}% ABV</strong>
              </div>

              <div className="meta-item">
                <span className="meta-label">Приготовление</span>
                <strong>
                  {selectedCocktail.preparation_time_minutes ?? "—"} мин.
                </strong>
              </div>

              <div className="meta-item">
                <span className="meta-label">Бокал</span>
                <strong>{selectedCocktail.glass || "—"}</strong>
              </div>
            </div>

            <div className="recipe-section">
              <h3>Ингредиенты</h3>

              <ul className="ingredients-list">
                {(selectedCocktail.ingredients || []).map(
                  (ingredient, index) => (
                    <li key={`${ingredient.name}-${index}`}>
                      <span>{ingredient.name}</span>
                      <strong>
                        {ingredient.amount
                          ? `${ingredient.amount} ${ingredient.unit || ""}`
                          : ingredient.note || "по вкусу"}
                      </strong>
                    </li>
                  )
                )}
              </ul>
            </div>

            <div className="recipe-section">
              <h3>Как приготовить</h3>
              <p className="instructions">
                {selectedCocktail.instructions_ru ||
                  selectedCocktail.instructions_en ||
                  "Инструкция пока не добавлена."}
              </p>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}

export default App;