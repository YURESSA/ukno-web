<template>
  <n-data-table
    pagination-behavior-on-filter="first"
    :columns="columns"
    :data="data"
    :pagination="pagination"
    :row-props="rowProps"
  />
</template>

<script setup>
import { NDataTable } from 'naive-ui'

const props = defineProps({
  data: Array,
  columns: Array
})

const emit = defineEmits(['row-click'])

const pagination = { pageSize: 10 }

const rowProps = (row) => ({
  style: 'cursor: pointer;',
  onClick: () => emit('row-click', row)
})
</script>


<style scoped>
:deep(.btn-delet){
  background: none;
  gap: 10px;
  max-height: 30px;
}

:deep(.icon){
  height: 15px;
  order: 1;
}

:deep(.text){
  order: 2;
}

:deep(.btn-delet:hover){
  background: #dc3545;
  color: white;
}

:deep(.btn-delet:hover > .text){
  color: white;
}

:deep(.btn-delet:hover .icon) {
  filter: brightness(0) invert(1);
}

:deep(.n-data-table-td){
  max-width: 400px;
}

</style>
