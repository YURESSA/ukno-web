<template>
  <section class="shop-banner-section">
    <div class="shop-banner-container">
      <div class="shop-banner-header">
        <div class="shop-title-wrapper">
          <div class="shop-logo-box">
            <h3 class="shop-heading">Магазин</h3>
          </div>
        </div>

        <RouterLink to="/shop" class="shop-details-link">
          <span>Подробнее о магазине</span>
          <svg
            class="arrow-icon"
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M5 12h14" />
            <path d="M13 6l6 6-6 6" />
          </svg>
        </RouterLink>
      </div>
      <div
        class="shop-card"
        @click="navigateToShop"
        role="button"
        tabindex="0"
        @keydown.enter="navigateToShop"
        aria-label="Перейти в магазин: У нас есть мерч!"
      >
        <img src="/shop-promo-line.svg" class="card-bg" alt="line" v-if="!$isMobile()">
        <div class="card-text-container">
          <h2 class="card-title larger-text">У нас есть мерч!</h2>
          <p class="card-subtitle text-l">
            Эксклюзивный мерч «Молодёжного Бюро» — твой главный аксессуар в этом сезоне.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateToShop = () => {
  router.push('/shop')
}
</script>

<style scoped>
.shop-banner-section {
  width: 100%;
  padding: 10px 30px 40px 30px;
  box-sizing: border-box;
}

.shop-banner-container {
  max-width: 1800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.shop-banner-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 4px;
  box-sizing: border-box;
}

.shop-title-wrapper {
  display: inline-flex;
  align-items: center;
}

.shop-logo-box {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.shop-details-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #F25C03;
  font-size: 20px;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  cursor: pointer;
}

.shop-details-link:hover {
  opacity: 0.85;
}

.shop-details-link:hover .arrow-icon {
  transform: translateX(4px);
}

.arrow-icon {
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.shop-card {
  position: relative;
  width: 100%;
  min-height: 190px;
  border-radius: 36px;
  background: linear-gradient(105deg, #F05000 0%, #F25C03 50%, #EC4F00 100%);
  padding: 44px 50px;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  box-shadow: 0 4px 20px rgba(242, 92, 3, 0.15);
}

.shop-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(242, 92, 3, 0.28);
}

.shop-card:focus-visible {
  outline: 3px solid #F25C03;
  outline-offset: 4px;
}

.card-text-container {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 680px;
}

.card-subtitle, .card-title {
  color: #FFFFFF;
}

@media screen and (max-width: 980px) {
  .shop-banner-section {
    padding: 10px 20px 30px 20px;
  }

  .shop-heading {
    font-size: 34px;
  }

  .shop-details-link {
    font-size: 16px;
    gap: 6px;
  }

  .arrow-icon {
    width: 18px;
    height: 18px;
  }

  .shop-card {
    min-height: 160px;
    padding: 32px 28px;
    border-radius: 26px;
  }

  .card-title {
    font-size: 26px;
  }

  .card-subtitle {
    font-size: 17px;
  }
}

@media screen and (max-width: 600px) {
  .shop-banner-section {
    padding: 5px 16px 24px 16px;
  }

  .shop-banner-header {
    flex-direction: row;
    align-items: center;
    gap: 12px;
  }

  .shop-heading {
    font-size: 26px;
  }

  .shop-details-link {
    font-size: 14px;
  }

  .arrow-icon {
    width: 16px;
    height: 16px;
  }

  .shop-card {
    padding: 24px 20px;
    border-radius: 20px;
    min-height: auto;
  }

  .card-text-container {
    gap: 10px;
  }

  .card-title {
    font-size: 22px;
  }

  .card-subtitle {
    font-size: 15px;
    line-height: 1.3;
  }
}
</style>
