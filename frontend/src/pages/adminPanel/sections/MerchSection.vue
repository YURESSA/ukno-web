<template>
  <div class="section-container">
    <!-- Вкладки -->
    <n-tabs v-model:value="activeTab" type="line" animated>
      <!-- ───────────── ТОВАРЫ ───────────── -->
      <n-tab-pane name="products" tab="Товары">
        <n-data-table
          :loading="loading"
          :columns="productColumns"
          :data="products"
          :row-props="productRowProps"
          :pagination="{ pageSize: 15 }"
        />
      </n-tab-pane>

      <!-- ───────────── КАТЕГОРИИ ───────────── -->
      <n-tab-pane name="categories" tab="Категории">
        <n-data-table
          :loading="loading"
          :columns="categoryColumns"
          :data="categories"
          :row-props="categoryRowProps"
          :pagination="{ pageSize: 20 }"
        />
      </n-tab-pane>

      <!-- ───────────── БАННЕРЫ ───────────── -->
      <n-tab-pane name="banners" tab="Баннеры">
        <n-data-table
          :loading="loading"
          :columns="bannerColumns"
          :data="banners"
          :row-props="bannerRowProps"
          :pagination="{ pageSize: 20 }"
        />
      </n-tab-pane>

      <!-- ───────────── ЗАКАЗЫ ───────────── -->
      <n-tab-pane name="orders" tab="Заказы">
        <n-data-table
          :loading="loading"
          :columns="orderColumns"
          :data="orders"
          :pagination="{ pageSize: 15 }"
        />
      </n-tab-pane>
    </n-tabs>

    <!-- ══════════════ МОДАЛКА: ТОВАР ══════════════ -->
    <n-modal
      v-model:show="showProductModal"
      preset="card"
      style="width: 860px"
      :title="isEdit ? 'Редактирование товара' : 'Создать товар'"
    >
      <n-form :model="productForm" label-placement="top">
        <n-grid :cols="2" :x-gap="20">
          <n-form-item-gi span="2" label="Название *">
            <n-input v-model:value="productForm.name" placeholder="Название товара" />
          </n-form-item-gi>

          <n-form-item-gi label="Категория">
            <n-select
              v-model:value="productForm.category_id"
              :options="categoryOptions"
              placeholder="Выберите категорию"
              clearable
            />
          </n-form-item-gi>

          <n-form-item-gi label="Цена, ₽ *">
            <n-input-number v-model:value="productForm.price" :min="0" style="width:100%" />
          </n-form-item-gi>

          <n-form-item-gi label="Коллекция">
            <n-input v-model:value="productForm.collection" placeholder="Например: Summer 2026" />
          </n-form-item-gi>

          <n-form-item-gi label="Активен">
            <n-switch v-model:value="productForm.is_active" />
          </n-form-item-gi>

          <n-form-item-gi span="2" label="Описание">
            <n-input
              v-model:value="productForm.description"
              type="textarea"
              :autosize="{ minRows: 3 }"
              placeholder="Описание товара..."
            />
          </n-form-item-gi>

          <!-- Цвета -->
          <n-form-item-gi span="2" label="Цвета и размеры">
            <div class="colors-list">
              <div v-for="(color, ci) in productForm.colors" :key="ci" class="color-block">
                <div class="color-block__header">
                  <n-input v-model:value="color.name" placeholder="Название цвета" style="width:180px" />
                  <n-color-picker v-model:value="color.hex_code" :show-alpha="false" style="width:120px" />
                  <n-button size="small" type="error" ghost @click="removeColor(ci)">✕</n-button>
                </div>
                <div class="sizes-list">
                  <div v-for="(size, si) in color.sizes" :key="si" class="size-row">
                    <n-input v-model:value="size.size_name" placeholder="Размер" style="width:100px" />
                    <n-input-number v-model:value="size.stock" :min="0" placeholder="Остаток" style="width:110px" />
                    <n-switch v-model:value="size.is_active" size="small" />
                    <n-button size="tiny" ghost @click="removeSize(ci, si)">✕</n-button>
                  </div>
                  <n-button size="small" dashed @click="addSize(ci)">+ Размер</n-button>
                </div>
              </div>
              <n-button dashed @click="addColor">+ Добавить цвет</n-button>
            </div>
          </n-form-item-gi>

          <!-- Фото -->
          <n-form-item-gi span="2" label="Фотографии">
            <n-upload
              multiple
              list-type="image-card"
              :default-file-list="productFileList"
              @change="handleProductUploadChange"
              @remove="handleProductRemove"
            >
              <n-upload-dragger>
                <n-icon size="28">+</n-icon>
              </n-upload-dragger>
            </n-upload>
          </n-form-item-gi>
        </n-grid>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button v-if="isEdit" type="error" ghost @click="confirmDeleteProduct">Удалить</n-button>
          <n-button @click="showProductModal = false">Отмена</n-button>
          <n-button type="primary" :loading="loading" @click="saveProduct">
            {{ isEdit ? 'Сохранить' : 'Создать' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- ══════════════ МОДАЛКА: КАТЕГОРИЯ ══════════════ -->
    <n-modal
      v-model:show="showCategoryModal"
      preset="card"
      style="width: 540px"
      :title="isEdit ? 'Редактирование категории' : 'Создать категорию'"
    >
      <n-form :model="categoryForm" label-placement="top">
        <n-grid :cols="2" :x-gap="20">
          <n-form-item-gi span="2" label="Название *">
            <n-input v-model:value="categoryForm.name" placeholder="Например: Футболки" />
          </n-form-item-gi>
          <n-form-item-gi label="Slug">
            <n-input v-model:value="categoryForm.slug" placeholder="tshirts" />
          </n-form-item-gi>
          <n-form-item-gi label="Порядок">
            <n-input-number v-model:value="categoryForm.order_index" :min="0" style="width:100%" />
          </n-form-item-gi>
          <n-form-item-gi span="2" label="Описание">
            <n-input v-model:value="categoryForm.description" type="textarea" :autosize="{ minRows: 2 }" />
          </n-form-item-gi>
          <n-form-item-gi label="Активна">
            <n-switch v-model:value="categoryForm.is_active" />
          </n-form-item-gi>
        </n-grid>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button v-if="isEdit" type="error" ghost @click="confirmDeleteCategory">Удалить</n-button>
          <n-button @click="showCategoryModal = false">Отмена</n-button>
          <n-button type="primary" :loading="loading" @click="saveCategory">
            {{ isEdit ? 'Сохранить' : 'Создать' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- ══════════════ МОДАЛКА: БАННЕР ══════════════ -->
    <n-modal
      v-model:show="showBannerModal"
      preset="card"
      style="width: 620px"
      :title="isEdit ? 'Редактирование баннера' : 'Создать баннер'"
    >
      <n-form :model="bannerForm" label-placement="top">
        <n-grid :cols="2" :x-gap="20">
          <n-form-item-gi span="2" label="Заголовок">
            <n-input v-model:value="bannerForm.title" placeholder="НОВЫЙ СТИЛЬ" />
          </n-form-item-gi>
          <n-form-item-gi span="2" label="Описание">
            <n-input v-model:value="bannerForm.description" type="textarea" :autosize="{ minRows: 2 }" placeholder="Текст под заголовком" />
          </n-form-item-gi>
          <n-form-item-gi label="Ссылка">
            <n-input v-model:value="bannerForm.link_url" placeholder="/shop/..." />
          </n-form-item-gi>
          <n-form-item-gi label="Порядок">
            <n-input-number v-model:value="bannerForm.order_index" :min="0" style="width:100%" />
          </n-form-item-gi>
          <n-form-item-gi label="Активен">
            <n-switch v-model:value="bannerForm.is_active" />
          </n-form-item-gi>
          <n-form-item-gi span="2" label="Изображение баннера">
            <n-upload
              :max="1"
              list-type="image-card"
              :default-file-list="bannerFileList"
              @change="handleBannerUploadChange"
            >
              <n-upload-dragger><n-icon size="28">+</n-icon></n-upload-dragger>
            </n-upload>
          </n-form-item-gi>
        </n-grid>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button v-if="isEdit" type="error" ghost @click="confirmDeleteBanner">Удалить</n-button>
          <n-button @click="showBannerModal = false">Отмена</n-button>
          <n-button type="primary" :loading="loading" @click="saveBanner">
            {{ isEdit ? 'Сохранить' : 'Создать' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, inject, watch, onMounted, h } from 'vue';
import axios from 'axios';
import {
  NTabs, NTabPane, NDataTable, NModal, NForm, NFormItemGi, NGrid,
  NInput, NInputNumber, NSelect, NSwitch, NColorPicker,
  NButton, NSpace, NAvatar, NUpload, NUploadDragger, NIcon,
  useMessage, useDialog
} from 'naive-ui';
import { useDataStore, baseUrl } from '@/stores/counter';

const store = useDataStore();
const message = useMessage();
const dialog = useDialog();
const loading = ref(false);
const activeTab = ref('products');

// ── Auth header ──────────────────────────────────────────────────────────────
const authHeaders = computed(() => ({ Authorization: `Bearer ${store.auth_key}` }));

// ═══════════════════════════════════════════════════════════════════════════════
// ТОВАРЫ
// ═══════════════════════════════════════════════════════════════════════════════
const products = ref([]);
const showProductModal = ref(false);
const isEdit = ref(false);
const productFileList = ref([]);
const newProductFiles = ref([]);

const productForm = ref(emptyProduct());

function emptyProduct() {
  return {
    product_id: null,
    name: '',
    description: '',
    price: 0,
    category_id: null,
    collection: '',
    is_active: true,
    colors: [],
  };
}

const productColumns = [
  { title: 'ID', key: 'product_id', width: 60 },
  {
    title: 'Фото', key: 'main_image', width: 80,
    render: (row) => row.main_image
      ? h(NAvatar, { size: 52, src: baseUrl + row.main_image, objectFit: 'cover', style: 'border-radius:8px' })
      : '—'
  },
  { title: 'Название', key: 'name', ellipsis: { tooltip: true } },
  { title: 'Категория', key: 'category', render: (row) => row.category?.name || '—', width: 140 },
  { title: 'Цена', key: 'price', render: (row) => `${Number(row.price).toLocaleString('ru')} ₽`, width: 120 },
  { title: 'Коллекция', key: 'collection', render: (row) => row.collection || '—', width: 150 },
  { title: 'Активен', key: 'is_active', render: (row) => row.is_active ? '✓' : '✗', width: 80 },
];

const productRowProps = (row) => ({
  style: 'cursor:pointer',
  onClick: () => openEditProduct(row),
});

async function fetchProducts() {
  loading.value = true;
  try {
    const { data } = await axios.get(`${baseUrl}api/admin/merch/products`, { headers: authHeaders.value });
    products.value = data.products || [];
  } finally { loading.value = false; }
}

async function openEditProduct(row) {
  isEdit.value = true;
  loading.value = true;
  try {
    const { data } = await axios.get(`${baseUrl}api/admin/merch/products/${row.product_id}`, { headers: authHeaders.value });
    productForm.value = {
      product_id: data.product_id,
      name: data.name || '',
      description: data.description || '',
      price: Number(data.price) || 0,
      category_id: data.category?.category_id || null,
      collection: data.collection || '',
      is_active: data.is_active ?? true,
      colors: (data.colors || []).map(c => ({
        color_id: c.color_id,
        name: c.name,
        hex_code: c.hex_code || '#000000',
        sizes: (c.sizes || []).map(s => ({
          variant_id: s.variant_id,
          size_name: s.size?.name || '',
          stock: s.stock ?? 0,
          is_active: s.is_active ?? true,
        })),
      })),
    };
    productFileList.value = (data.images || []).map((img, i) => ({
      id: `old-${img.image_id}`,
      name: `Фото ${i + 1}`,
      status: 'finished',
      url: baseUrl + img.image_path,
    }));
    newProductFiles.value = [];
    showProductModal.value = true;
  } catch (e) {
    message.error(e.response?.data?.message || 'Ошибка загрузки данных товара');
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function openCreateProduct() {
  isEdit.value = false;
  productForm.value = emptyProduct();
  productFileList.value = [];
  newProductFiles.value = [];
  showProductModal.value = true;
}

function addColor() { productForm.value.colors.push({ name: '', hex_code: '#000000', sizes: [] }); }
function removeColor(i) { productForm.value.colors.splice(i, 1); }
function addSize(ci) { productForm.value.colors[ci].sizes.push({ size_name: '', stock: 0, is_active: true }); }
function removeSize(ci, si) { productForm.value.colors[ci].sizes.splice(si, 1); }

function handleProductUploadChange({ fileList }) {
  productFileList.value = fileList;
  newProductFiles.value = fileList.filter(f => f.file).map(f => f.file);
}

async function handleProductRemove({ file }) {
  if (!file.id.toString().startsWith('old-')) {
    newProductFiles.value = newProductFiles.value.filter(f => f.name !== file.name);
    return true;
  }
  return new Promise(resolve => {
    dialog.warning({
      title: 'Удалить фото?',
      positiveText: 'Удалить',
      negativeText: 'Отмена',
      onPositiveClick: async () => {
        const imageId = parseInt(file.id.replace('old-', ''));
        try {
          await axios.delete(
            `${baseUrl}api/admin/merch/products/${productForm.value.product_id}/images/${imageId}`,
            { headers: authHeaders.value }
          );
          message.success('Фото удалено');
          resolve(true);
        } catch { message.error('Ошибка удаления фото'); resolve(false); }
      },
      onNegativeClick: () => resolve(false),
    });
  });
}

async function saveProduct() {
  if (!productForm.value.name.trim()) return message.warning('Название обязательно');
  loading.value = true;
  try {
    const fd = new FormData();
    const payload = {
      name: productForm.value.name,
      description: productForm.value.description,
      price: productForm.value.price,
      category_id: productForm.value.category_id,
      collection: productForm.value.collection,
      is_active: productForm.value.is_active,
      colors: productForm.value.colors,
    };
    fd.append('data', JSON.stringify(payload));
    newProductFiles.value.forEach(f => fd.append('images', f.file || f));

    if (isEdit.value) {
      await axios.put(
        `${baseUrl}api/admin/merch/products/${productForm.value.product_id}`,
        fd, { headers: { ...authHeaders.value, 'Content-Type': 'multipart/form-data' } }
      );
      message.success('Товар обновлён');
    } else {
      await axios.post(`${baseUrl}api/admin/merch/products`, fd, {
        headers: { ...authHeaders.value, 'Content-Type': 'multipart/form-data' }
      });
      message.success('Товар создан');
    }
    showProductModal.value = false;
    await fetchProducts();
  } catch (e) {
    message.error(e.response?.data?.message || 'Ошибка сохранения');
  } finally { loading.value = false; }
}

function confirmDeleteProduct() {
  dialog.warning({
    title: 'Удалить товар?',
    content: `"${productForm.value.name}" будет удалён безвозвратно`,
    positiveText: 'Удалить', negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.delete(`${baseUrl}api/admin/merch/products/${productForm.value.product_id}`, { headers: authHeaders.value });
        message.success('Товар удалён');
        showProductModal.value = false;
        await fetchProducts();
      } catch { message.error('Ошибка удаления'); }
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// КАТЕГОРИИ
// ═══════════════════════════════════════════════════════════════════════════════
const categories = ref([]);
const showCategoryModal = ref(false);
const categoryForm = ref(emptyCategory());

function emptyCategory() {
  return { category_id: null, name: '', slug: '', description: '', order_index: 0, is_active: true };
}

const categoryOptions = computed(() =>
  categories.value.map(c => ({ label: c.name, value: c.category_id }))
);

const categoryColumns = [
  { title: 'ID', key: 'category_id', width: 60 },
  { title: 'Название', key: 'name' },
  { title: 'Slug', key: 'slug', width: 160 },
  { title: 'Порядок', key: 'order_index', width: 100 },
  { title: 'Активна', key: 'is_active', render: (row) => row.is_active ? '✓' : '✗', width: 90 },
];

const categoryRowProps = (row) => ({
  style: 'cursor:pointer',
  onClick: () => {
    isEdit.value = true;
    categoryForm.value = { ...row };
    showCategoryModal.value = true;
  }
});

async function fetchCategories() {
  const { data } = await axios.get(`${baseUrl}api/admin/merch/categories`, { headers: authHeaders.value });
  categories.value = data.categories || [];
}

async function saveCategory() {
  if (!categoryForm.value.name.trim()) return message.warning('Название обязательно');
  loading.value = true;
  try {
    if (isEdit.value) {
      await axios.put(`${baseUrl}api/admin/merch/categories/${categoryForm.value.category_id}`,
        categoryForm.value, { headers: authHeaders.value });
      message.success('Категория обновлена');
    } else {
      await axios.post(`${baseUrl}api/admin/merch/categories`, categoryForm.value, { headers: authHeaders.value });
      message.success('Категория создана');
    }
    showCategoryModal.value = false;
    await fetchCategories();
  } catch (e) {
    message.error(e.response?.data?.message || 'Ошибка');
  } finally { loading.value = false; }
}

function confirmDeleteCategory() {
  dialog.warning({
    title: 'Удалить категорию?',
    positiveText: 'Удалить', negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.delete(`${baseUrl}api/admin/merch/categories/${categoryForm.value.category_id}`, { headers: authHeaders.value });
        message.success('Удалено');
        showCategoryModal.value = false;
        await fetchCategories();
      } catch { message.error('Ошибка'); }
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// БАННЕРЫ
// ═══════════════════════════════════════════════════════════════════════════════
const banners = ref([]);
const showBannerModal = ref(false);
const bannerForm = ref(emptyBanner());
const bannerFileList = ref([]);
const newBannerFile = ref(null);

function emptyBanner() {
  return { banner_id: null, title: '', description: '', link_url: '', order_index: 0, is_active: true };
}

const bannerColumns = [
  { title: 'ID', key: 'banner_id', width: 60 },
  {
    title: 'Изображение', key: 'image_path', width: 90,
    render: (row) => row.image_path
      ? h(NAvatar, { size: 56, src:baseUrl + row.image_path, objectFit: 'cover', style: 'border-radius:8px' })
      : '—'
  },
  { title: 'Заголовок', key: 'title', ellipsis: { tooltip: true } },
  { title: 'Ссылка', key: 'link_url', ellipsis: { tooltip: true }, width: 200 },
  { title: 'Порядок', key: 'order_index', width: 90 },
  { title: 'Активен', key: 'is_active', render: (row) => row.is_active ? '✓' : '✗', width: 80 },
];

const bannerRowProps = (row) => ({
  style: 'cursor:pointer',
  onClick: () => {
    isEdit.value = true;
    bannerForm.value = { ...row };
    bannerFileList.value = row.image_path
      ? [{ id: 'old-0', name: 'Изображение', status: 'finished', url: baseUrl + row.image_path }]
      : [];
    newBannerFile.value = null;
    showBannerModal.value = true;
  }
});

async function fetchBanners() {
  const { data } = await axios.get(`${baseUrl}api/admin/merch/banners`, { headers: authHeaders.value });
  banners.value = data.banners || [];
}

function handleBannerUploadChange({ fileList }) {
  bannerFileList.value = fileList;
  const newFile = fileList.find(f => f.file);
  newBannerFile.value = newFile ? (newFile.file?.file || newFile.file) : null;
}

async function saveBanner() {
  loading.value = true;
  try {
    const fd = new FormData();
    const payload = {
      title: bannerForm.value.title,
      description: bannerForm.value.description,
      link_url: bannerForm.value.link_url,
      order_index: bannerForm.value.order_index,
      is_active: bannerForm.value.is_active,
    };
    fd.append('data', JSON.stringify(payload));
    if (newBannerFile.value) fd.append('image', newBannerFile.value);

    if (isEdit.value) {
      await axios.put(`${baseUrl}api/admin/merch/banners/${bannerForm.value.banner_id}`, fd, {
        headers: { ...authHeaders.value, 'Content-Type': 'multipart/form-data' }
      });
      message.success('Баннер обновлён');
    } else {
      await axios.post(`${baseUrl}api/admin/merch/banners`, fd, {
        headers: { ...authHeaders.value, 'Content-Type': 'multipart/form-data' }
      });
      message.success('Баннер создан');
    }
    showBannerModal.value = false;
    await fetchBanners();
  } catch (e) {
    message.error(e.response?.data?.message || 'Ошибка');
  } finally { loading.value = false; }
}

function confirmDeleteBanner() {
  dialog.warning({
    title: 'Удалить баннер?',
    positiveText: 'Удалить', negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.delete(`${baseUrl}api/admin/merch/banners/${bannerForm.value.banner_id}`, { headers: authHeaders.value });
        message.success('Удалено');
        showBannerModal.value = false;
        await fetchBanners();
      } catch { message.error('Ошибка'); }
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// ЗАКАЗЫ
// ═══════════════════════════════════════════════════════════════════════════════
const orders = ref([]);

const orderColumns = [
  { title: 'ID', key: 'order_id', width: 70 },
  { title: 'Покупатель', key: 'contact_channel', ellipsis: { tooltip: true }, width: 200 },
  {
    title: 'Статус', key: 'status', width: 160,
    render: (row) => {
      const labels = { new: 'Новый', awaiting_payment: 'Ожидает оплаты', paid: 'Оплачен', cancelled: 'Отменён', completed: 'Выдан' };
      return labels[row.status] || row.status;
    }
  },
  {
    title: 'Сумма', key: 'total_price', width: 120,
    render: (row) => `${Number(row.total_price).toLocaleString('ru')} ₽`
  },
  {
    title: 'Товары', key: 'items',
    render: (row) => (row.items || []).map(i => `${i.product_name} × ${i.quantity}`).join(', ')
  },
  {
    title: 'Дата', key: 'created_at', width: 130,
    render: (row) => row.created_at ? new Date(row.created_at).toLocaleDateString('ru-RU') : '—'
  },
];

async function fetchOrders() {
  loading.value = true;
  try {
    const { data } = await axios.get(`${baseUrl}api/admin/merch/orders`, { headers: authHeaders.value });
    orders.value = data.orders || [];
  } finally { loading.value = false; }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ADD-EVENT из PanelLayout (кнопка «+ Создать запись»)
// ═══════════════════════════════════════════════════════════════════════════════
const addTrigger = inject('admin-add-event');
watch(addTrigger, () => {
  isEdit.value = false;
  if (activeTab.value === 'products') openCreateProduct();
  else if (activeTab.value === 'categories') {
    categoryForm.value = emptyCategory();
    showCategoryModal.value = true;
  } else if (activeTab.value === 'banners') {
    bannerForm.value = emptyBanner();
    bannerFileList.value = [];
    newBannerFile.value = null;
    showBannerModal.value = true;
  }
});

onMounted(async () => {
  await Promise.all([fetchProducts(), fetchCategories(), fetchBanners(), fetchOrders()]);
});
</script>

<style scoped>
.section-container { padding: 4px 0; }

.colors-list { display: flex; flex-direction: column; gap: 16px; width: 100%; }

.color-block {
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.color-block__header { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.sizes-list { display: flex; flex-direction: column; gap: 8px; padding-left: 8px; }

.size-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
</style>
