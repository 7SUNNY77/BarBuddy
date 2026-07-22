import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = "https://barbuddy-api.onrender.com/api/cocktails";

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

const INGREDIENT_TRANSLATIONS = {
  "100% Agave Tequila": "Текила 100% агавы",
  "Absinthe": "Абсент",
  "Agave Syrup": "Сироп агавы",
  "Aged Rum": "Выдержанный ром",
  "Amaretto": "Амаретто",
  "Amaro Nonino": "Амаро Нонино",
  "Amber Jamaican Rum": "Ямайский янтарный ром",
  "Angostura Bitters": "Биттер Ангостура",
  "Aperol": "Апероль",
  "Apricot Brandy": "Абрикосовый бренди",
  "Aromatic Bitters": "Ароматический биттер",
  "Bénédictine": "Бенедиктин",
  "Bitter Campari": "Горький Кампари",
  "Blended Scotch Whisky": "Купажированный шотландский виски",
  "Bourbon Whisky": "Бурбон",
  "Bourbon or Rye Whiskey": "Бурбон или ржаной виски",
  "Brandy": "Бренди",
  "Brut Champagne or Prosecco": "Брют шампанское или просекко",
  "Cachaça": "Кашаса",
  "Calvados": "Кальвадос",
  "Celery Salt": "Сельдерейная соль",
  "Chamomile cordial": "Ромашковый кордиал",
  "Champagne": "Шампанское",
  "Cherry liqueur": "Вишнёвый ликёр",
  "Chilled Champagne": "Охлаждённое шампанское",
  "Coca Cola": "Кока-кола",
  "Coconut Cream": "Кокосовые сливки",
  "Coffee Liqueur": "Кофейный ликёр",
  "Cognac": "Коньяк",
  "Cognac or Brandy": "Коньяк или бренди",
  "Cointreau": "Куантро",
  "Cola": "Кола",
  "Cranberry Juice": "Клюквенный сок",
  "Cream": "Сливки",
  "Crème de Cassis": "Крем де Кассис",
  "Crème de Cacao": "Крем де Какао",
  "Crème de Cassis": "Крем де Кассис",
  "Crème de Menthe": "Крем де Мент",
  "Crème de Mûre": "Крем де Мюр",
  "Crème de Violette": "Крем де Виолет",
  "Cuban Aguardiente": "Кубинский агуардиенте",
  "Curacao": "Кюрасао",
  "DOM Bénédictine": "DOM Бенедиктин",
  "Demerara Rum": "Ром Демерара",
  "Donn's Mix": "Смесь Донна",
  "Drambuie": "Драмбуи",
  "Dry Gin": "Сухой джин",
  "Dry Vermouth": "Сухой вермут",
  "Dry White Wine": "Сухое белое вино",
  "Egg White": "Яичный белок",
  "Egg Yolk": "Яичный желток",
  "Egg white": "Яичный белок",
  "Elderflower Cordial": "Кордиал из бузины",
  "Espadin Mezcal": "Мескаль Эспадин",
  "Falernum": "Фалернум",
  "Fernet Branca": "Фернет-Бранка",
  "Fresh Cream": "Свежие сливки",
  "Fresh Lemon Juice": "Свежевыжатый лимонный сок",
  "Fresh Lime": "Свежий лайм",
  "Fresh Lime Juice": "Свежевыжатый сок лайма",
  "Fresh Orange Juice": "Свежевыжатый апельсиновый сок",
  "Fresh Pineapple Juice": "Свежевыжатый ананасовый сок",
  "Freshly Squeezed Lime Juice": "Свежевыжатый сок лайма",
  "Galliano": "Гальяно",
  "Gin": "Джин",
  "Ginger Ale": "Имбирный эль",
  "Ginger Beer": "Имбирное пиво",
  "Gold Puerto Rican rum": "Золотой пуэрто-риканский ром",
  "Gold Rum": "Золотой ром",
  "Goslings Rum": "Ром Goslings",
  "Grand Marnier": "Гран Марнье",
  "Grapefruit Juice": "Грейпфрутовый сок",
  "Green Chartreuse": "Зелёный шартрез",
  "Grenadine Syrup": "Сироп гренадин",
  "Honey Syrup": "Медовый сироп",
  "Honey mix": "Медовая смесь",
  "Hot coffee": "Горячий кофе",
  "Irish Whiskey": "Ирландский виски",
  "Jamaica Overproof White Rum": "Ямайский крепкий белый ром",
  "Jamaican Rum": "Ямайский ром",
  "Jamaican dark rum": "Ямайский тёмный ром",
  "Kahlúa": "Калуа",
  "Lagavulin 16 y Whisky": "Виски Lagavulin 16 лет",
  "Lemon juice": "Лимонный сок",
  "Lillet Blanc": "Лилле Блан",
  "Lime Juice": "Сок лайма",
  "Lime cut into small wedges": "Лайм, нарезанный небольшими дольками",
  "London Dry Gin": "Лондонский сухой джин",
  "Maraschino Liqueur": "Ликёр Мараскино",
  "Maraschino Luxardo": "Мараскино Luxardo",
  "Martinique Molasses Rhum": "Мартиникский ром из мелассы",
  "Mezcal": "Мескаль",
  "Mint Leaves": "Листья мяты",
  "Mint Sprigs": "Веточки мяты",
  "Monin Honey Syrup": "Медовый сироп Monin",
  "Old Tom Gin": "Джин Олд Том",
  "Orange Bitters": "Апельсиновый биттер",
  "Orange Curacao": "Апельсиновый кюрасао",
  "Orange Flower Water": "Апельсиновая цветочная вода",
  "Orgeat Syrup": "Сироп оршад",
  "Peach Schnapps": "Персиковый шнапс",
  "Pepper": "Перец",
  "Pernod": "Перно",
  "Peychaud's Bitters": "Биттер Пейшо",
  "Pink Grapefruit Soda": "Розовая грейпфрутовая содовая",
  "Pisco": "Писко",
  "Plain Water": "Вода",
  "Powdered Sugar": "Сахарная пудра",
  "Prosecco": "Просекко",
  "Raspberry Liqueur": "Малиновый ликёр",
  "Raspberry Syrup": "Малиновый сироп",
  "Raw Egg White": "Сырой яичный белок",
  "Raw Honey": "Натуральный мёд",
  "Red Tawny Port Wine": "Красный портвейн Тони",
  "Red wine": "Красное вино",
  "Rum": "Ром",
  "Rye Whiskey or Bourbon": "Ржаной виски или бурбон",
  "Rye Whisky": "Ржаной виски",
  "Salt": "Соль",
  "Scotch Whisky": "Шотландский виски",
  "Simple Syrup": "Сахарный сироп",
  "Smirnoff Vodka": "Водка Smirnoff",
  "Soda Water": "Содовая",
  "Sparkling wine": "Игристое вино",
  "Sugar": "Сахар",
  "Sugar Cane Juice": "Сок сахарного тростника",
  "Sugar Cube": "Кубик сахара",
  "Sugar Syrup": "Сахарный сироп",
  "Superfine Sugar": "Мелкий сахар",
  "Sweet Red Vermouth": "Сладкий красный вермут",
  "Sweet Vermouth": "Сладкий вермут",
  "Tabasco": "Табаско",
  "Tequila": "Текила",
  "Tequila 100% Agave": "Текила 100% агавы",
  "Tequila Agave 100% Reposado": "Текила репосадо 100% агавы",
  "Tomato Juice": "Томатный сок",
  "Triple Sec": "Трипл-сек",
  "Vanilla Extract": "Экстракт ванили",
  "Vodka": "Водка",
  "Vodka Citron": "Цитрусовая водка",
  "Vodka Vanilla": "Ванильная водка",
  "Water": "Вода",
  "White Cane Sugar": "Белый тростниковый сахар",
  "White Crème de Menthe": "Белый крем де мент",
  "White Cuban Ron": "Белый кубинский ром",
  "White Peach Puree": "Пюре из белого персика",
  "White Rum": "Белый ром",
  "White Smooth Grappa": "Белая мягкая граппа",
  "Worcestershire Sauce": "Вустерский соус",
  "Yellow Chartreuse": "Жёлтый шартрез",
  "fresh Mint sprigs": "Свежие веточки мяты",
  "quarter size Sliced Fresh Ginger": "Ломтики свежего имбиря",
  "strong Espresso": "Крепкий эспрессо",
  "thin Slices Red Chili Pepper": "Тонкие ломтики красного перца чили",
};

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
  const [recommendationReason, setRecommendationReason] = useState("");
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState("");

  const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const userName = telegramUser?.first_name;

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
        setError(
          `Не удалось загрузить каталог: ${requestError.message}`
        );
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

  async function getRecommendations() {
    const query = recommendationQuery.trim();

    if (!query) {
      setRecommendations([]);
      setRecommendationReason("");
      setRecommendationVisible(true);
      return;
    }

    try {
      setRecommendationLoading(true);
      setRecommendationVisible(true);
      setRecommendationReason("");

      const response = await fetch(`${API_URL}/recommendations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка AI-подбора: ${response.status}`);
      }

      const data = await response.json();

      setRecommendations(data.recommendations || []);
      setRecommendationReason(data.reason || "");
    } catch (requestError) {
      console.error(requestError);
      setRecommendations([]);
      setRecommendationReason("");
      setError(
        "Не удалось подобрать коктейли. Попробуйте ещё раз."
      );
    } finally {
      setRecommendationLoading(false);
    }
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

          <button
            type="button"
            onClick={getRecommendations}
            disabled={recommendationLoading}
          >
            {recommendationLoading ? "Подбираем..." : "Подобрать"}
          </button>
        </div>

        <p className="recommendation-hint">
          Попробуй: «сладкое и кофейное», «что-то с ромом», «лёгкое с цитрусом».
        </p>

        {recommendationVisible && (
          <div className="recommendation-results">
            {recommendationLoading ? (
              <p className="recommendation-empty">
                AI подбирает коктейли...
              </p>
            ) : recommendations.length > 0 ? (
              <>
                {recommendationReason && (
                  <p className="ai-recommendation-reason">
                    {recommendationReason}
                  </p>
                )}

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

                      <span className="recommendation-reason">
                        Подходит: {(cocktail.taste_tags || [])
                          .slice(0, 3)
                          .join(", ")}
                      </span>
                    </button>
                  ))}
                </div>
              </>
            ) : (
              <p className="recommendation-empty">
                Не нашёл подходящих вариантов. Попробуй описать вкус,
                крепость или исключить конкретный ингредиент.
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
                {selectedCocktail.ingredients.map((ingredient, index) => {
                  if (typeof ingredient === "string") {
                    return <li key={`${ingredient}-${index}`}>{ingredient}</li>;
                  }

                  const originalName =
                    ingredient.name || ingredient.ingredient || "Ингредиент";

                  const name =
                    INGREDIENT_TRANSLATIONS[originalName] || originalName;
                  const amount = ingredient.amount || ingredient.quantity || "";
                  const unit = ingredient.unit || "";

                  return (
                    <li className="ingredient-row" key={`${name}-${index}`}>
                      <span className="ingredient-name">{name}</span>

                      {(amount || unit) && (
                        <span className="ingredient-amount">
                          {[amount, unit].filter(Boolean).join(" ")}
                        </span>
                      )}
                    </li>
                  );
                })}
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