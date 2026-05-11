import Vue from 'vue';
import api from '../api';

const placeholderImage = 'https://picsum.photos/400/240';

const state = Vue.observable({
  slider: [],
  tutorial: null,
  categories: [],
  resources: [],
  selectedCategoryId: undefined,
  profile: { display_name: '微信用户', balance_cents: 0 },
  files: [],
  orders: [],
  addresses: [],
  uploadProgress: 0,
  priceTip: '',
  loadState: {
    home: false,
    library: false,
    me: false
  }
});

function notify(title, icon) {
  uni.showToast({
    title,
    icon: icon || 'none',
    duration: 1800
  });
}

function confirmDialog(content, title) {
  return new Promise((resolve) => {
    uni.showModal({
      title: title || '提示',
      content,
      success: (result) => resolve(!!result.confirm),
      fail: () => resolve(false)
    });
  });
}

function promptRename(currentName) {
  return new Promise((resolve) => {
    uni.showModal({
      title: '重命名文件',
      editable: true,
      placeholderText: currentName,
      success: (result) => {
        if (!result.confirm) {
          resolve(null);
          return;
        }
        const value = typeof result.content === 'string' ? result.content.trim() : '';
        resolve(value || null);
      },
      fail: () => resolve(null)
    });
  });
}

function chooseMessageFile() {
  return new Promise((resolve, reject) => {
    uni.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf'],
      success: resolve,
      fail: reject
    });
  });
}

function uploadFile(url, filePath, formData) {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url,
      filePath,
      name: 'file',
      formData,
      success: resolve,
      fail: reject
    });
  });
}

function downloadFile(url) {
  return new Promise((resolve, reject) => {
    uni.downloadFile({
      url,
      success: resolve,
      fail: reject
    });
  });
}

async function loadHome(force) {
  if (state.loadState.home && !force) return;

  try {
    const responses = await Promise.all([
      api.get('/v1/home/slider'),
      api.get('/v1/home/tutorial'),
      api.get('/v1/prices/tip')
    ]);
    state.slider = responses[0].data || [];
    state.tutorial = responses[1].data || null;
    state.priceTip = (responses[2].data && responses[2].data.text) || '';
  } catch (e) {
    state.slider = [];
    state.tutorial = { title: '新手打印说明', updated_at: '请稍后同步' };
  }

  state.loadState.home = true;
}

async function loadLibrary(force) {
  if (state.loadState.library && !force) return;

  try {
    const categoriesResponse = await api.get('/v1/library/categories');
    state.categories = categoriesResponse.data || [];

    if (state.categories.length) {
      state.selectedCategoryId = state.categories[0].id;
      await selectCategory(state.categories[0].id);
    }
  } catch (e) {
    state.categories = [];
    state.resources = [];
  }

  state.loadState.library = true;
}

async function loadMe(force) {
  if (state.loadState.me && !force) return;

  try {
    const responses = await Promise.all([
      api.get('/v1/users/me'),
      api.get('/v1/files'),
      api.get('/v1/orders'),
      api.get('/v1/addresses')
    ]);

    state.profile = Object.assign({}, state.profile, responses[0].data || {});
    state.files = (responses[1].data && responses[1].data.items) || [];
    state.orders = (responses[2].data && responses[2].data.items) || [];
    state.addresses = responses[3].data || [];
  } catch (e) {
    state.profile = { display_name: '微信用户', balance_cents: 0 };
    state.files = [];
    state.orders = [];
    state.addresses = [];
  }

  state.loadState.me = true;
}

async function selectCategory(categoryId) {
  state.selectedCategoryId = categoryId;
  const response = await api.get('/v1/library/resources', { params: { category_id: categoryId } });
  state.resources = (response.data && (response.data.items || response.data)) || [];
}

function openTutorial() {
  uni.showModal({
    title: '打印教程',
    content: state.tutorial && state.tutorial.title
      ? state.tutorial.title + '\n最近更新：' + (state.tutorial.updated_at || '-')
      : '教程内容加载中',
    showCancel: false
  });
}

function openPrices() {
  uni.showModal({
    title: '价格列表',
    content: state.priceTip || '价格说明会在接入后展示。',
    showCancel: false
  });
}

function previewResource(resource) {
  uni.showModal({
    title: resource.title || '资料预览',
    content: String(resource.page_count || '-') + ' 页资料，支持在线预览与直接下单。',
    showCancel: false
  });
}

async function createFromResource(resource) {
  try {
    await api.post('/v1/orders/create-from-resource', {
      resource_id: resource.id,
      options: { size: 'A4', color: 'black_white', duplex: false, copies: 1 }
    });
    notify('资料已加入订单', 'success');
    state.loadState.me = false;
    await loadMe(true);
  } catch (e) {
    notify('下单失败，请稍后重试');
  }
}

function getOrderStatusCards() {
  const by = (statuses) => state.orders.filter((order) => statuses.indexOf(order.status) !== -1).length;
  return [
    { key: 'PENDING_PAYMENT', label: '待付款', count: by(['CREATED', 'PENDING_PAYMENT']) },
    { key: 'PENDING_PRINT', label: '待打印', count: by(['PAID', 'PROCESSING']) },
    { key: 'TO_RECEIVE', label: '待收货', count: by(['PRINTED', 'SHIPPED']) },
    { key: 'COMPLETED', label: '已完成', count: by(['COMPLETED']) },
    { key: 'AFTER_SALES', label: '退款/售后', count: by(['REFUNDED', 'CANCELLED']) }
  ];
}

async function chooseAndUploadFile() {
  try {
    const result = await chooseMessageFile();
    const file = result.tempFiles && result.tempFiles[0];
    if (!file) return;

    if (file.size > 50 * 1024 * 1024) {
      notify('文件过大，不能超过 50MB');
      return;
    }

    const create = await api.post('/v1/files/create-upload', {
      filename: file.name,
      size: file.size,
      content_type: file.type || 'application/pdf'
    });

    state.uploadProgress = 15;
    await uploadFile(create.data.upload_url, file.path || file.tempFilePath, create.data.fields || {});
    state.uploadProgress = 90;
    await api.post('/v1/files/complete', { upload_id: create.data.upload_id });
    state.uploadProgress = 100;
    notify('文件上传成功', 'success');
    state.loadState.me = false;
    await loadMe(true);
  } catch (e) {
    notify('文件上传失败，请稍后重试');
  }
}

async function previewFile(file) {
  try {
    const result = await api.get('/v1/files/' + file.id + '/download');
    const downloadResult = await downloadFile(result.data.url);

    if (downloadResult.tempFilePath) {
      uni.openDocument({ filePath: downloadResult.tempFilePath, showMenu: true });
      return;
    }

    notify('预览文件失败');
  } catch (e) {
    notify('预览文件失败');
  }
}

async function createOrderForFile(file) {
  const confirmed = await confirmDialog('确认按默认设置为 ' + file.filename + ' 下单吗？');
  if (!confirmed) return;

  try {
    await api.post('/v1/orders/create', {
      items: [{ file_id: file.id, options: { size: 'A4', color: 'black_white', duplex: false, copies: 1 } }]
    });
    notify('订单已创建', 'success');
    state.loadState.me = false;
    await loadMe(true);
  } catch (e) {
    notify('下单失败，请稍后重试');
  }
}

async function deleteFile(file) {
  const confirmed = await confirmDialog('确认删除这个文件吗？');
  if (!confirmed) return;

  try {
    await api.delete('/v1/files/' + file.id);
    notify('文件已删除', 'success');
    state.loadState.me = false;
    await loadMe(true);
  } catch (e) {
    notify('删除失败，请稍后重试');
  }
}

async function renameFile(file) {
  const filename = await promptRename(file.filename);
  if (!filename || filename === file.filename) return;

  try {
    await api.patch('/v1/files/' + file.id, { filename });
    notify('文件已重命名', 'success');
    state.loadState.me = false;
    await loadMe(true);
  } catch (e) {
    notify('重命名失败，请稍后重试');
  }
}

function filterOrdersByStatus(status) {
  const filtered = state.orders.filter((order) => {
    if (status === 'ALL') return true;
    if (status === 'PENDING_PAYMENT') return ['CREATED', 'PENDING_PAYMENT'].indexOf(order.status) !== -1;
    if (status === 'PENDING_PRINT') return ['PAID', 'PROCESSING'].indexOf(order.status) !== -1;
    if (status === 'TO_RECEIVE') return ['PRINTED', 'SHIPPED'].indexOf(order.status) !== -1;
    if (status === 'COMPLETED') return ['COMPLETED'].indexOf(order.status) !== -1;
    return ['REFUNDED', 'CANCELLED'].indexOf(order.status) !== -1;
  });

  notify(status === 'ALL' ? '共 ' + filtered.length + ' 条订单' : '已筛选 ' + filtered.length + ' 条订单');
}

async function logout() {
  try {
    await api.post('/v1/auth/logout', {});
  } catch (e) {
    // ignore logout network error
  }

  uni.removeStorageSync('token');
  state.profile = { display_name: '微信用户', balance_cents: 0 };
  state.files = [];
  state.orders = [];
  notify('已退出登录', 'success');
}

function openCustomerService() {
  notify('客服功能待接入');
}

function goToMeTab() {
  uni.switchTab({ url: '/pages/me/index' });
}

export function useMiniStore() {
  return {
    state,
    placeholderImage,
    loadHome,
    loadLibrary,
    loadMe,
    selectCategory,
    openTutorial,
    openPrices,
    previewResource,
    createFromResource,
    chooseAndUploadFile,
    previewFile,
    createOrderForFile,
    deleteFile,
    renameFile,
    filterOrdersByStatus,
    logout,
    openCustomerService,
    goToMeTab,
    getOrderStatusCards
  };
}
