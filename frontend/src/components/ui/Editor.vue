<template>
  <div v-if="editor" class="editor-wrapper">
    <div class="toolbar">
      <n-space :size="[4, 8]" align="center">
        <n-button-group>
          <n-button
            @click="editor.chain().focus().undo().run()"
            :disabled="!editor.can().undo()"
            title="Отменить (Ctrl+Z)"
          >
            ↩️
          </n-button>
          <n-button
            @click="editor.chain().focus().redo().run()"
            :disabled="!editor.can().redo()"
            title="Вернуть (Ctrl+Y)"
          >
            ↪️
          </n-button>
        </n-button-group>

        <n-divider vertical />

        <n-button-group>
          <n-button
            :secondary="!editor.isActive('paragraph')"
            @click="editor.chain().focus().setParagraph().run()"
            title="Обычный текст"
          >
            ¶
          </n-button>
          <n-button
            :secondary="!editor.isActive('heading', { level: 4 })"
            @click="editor.chain().focus().toggleHeading({ level: 4 }).run()"
            title="Заголовок 1"
          >
            Заголовок 1
          </n-button>
          <n-button
            :secondary="!editor.isActive('heading', { level: 5 })"
            @click="editor.chain().focus().toggleHeading({ level: 5 }).run()"
            title="Заголовок 2"
          >
            Заголовок 2
          </n-button>
        </n-button-group>

        <n-divider vertical />

        <n-button-group>
          <n-button
            :secondary="!editor.isActive('bold')" @click="editor.chain().focus().toggleBold().run()"
            title="Жирный"
          >
            <b>B</b>
          </n-button>
          <n-button
            :secondary="!editor.isActive('italic')" @click="editor.chain().focus().toggleItalic().run()"
            title="Курсив"
          >
            <i>I</i>
          </n-button>
        </n-button-group>

        <n-divider vertical />

        <n-button-group>
          <n-button
            :secondary="!editor.isActive('bulletList')" @click="editor.chain().focus().toggleBulletList().run()"
            title="Список с точками"
          >
            • Точки
          </n-button>
          <n-button
            :secondary="!editor.isActive('orderedList')" @click="editor.chain().focus().toggleOrderedList().run()"
            title="Список с цифрами"
          >
            1. Числа
          </n-button>
          <n-button
            :secondary="!editor.isActive('blockquote')" @click="editor.chain().focus().toggleBlockquote().run()"
            title="Выделить как цитату"
          >
            “ Цитата
          </n-button>
        </n-button-group>

        <n-divider vertical />

        <n-button
          :secondary="!editor.isActive('link')"
          @click="setLink"
          title="Выделить текст как ссылку"
        >
          🔗 Ссылка
        </n-button>
      </n-space>
    </div>

    <editor-content :editor="editor" class="tiptap-content" />
  </div>
</template>

<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import { watch } from 'vue'
import { NButton, NButtonGroup, NSpace, NDivider } from 'naive-ui'

const props = defineProps({
  modelValue: { type: String, default: '' }
})
const emit = defineEmits(['update:modelValue'])

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({
      // Настройка для того, чтобы Enter всегда создавал новый параграф <p>,
      // а не просто <br> внутри одного блока.
      heading: {
        levels: [4, 5],
      },
    }),
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        class: 'editor-link',
        rel: 'noopener noreferrer',
        target: '_blank',
      },
    }),
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

const setLink = () => {
  const previousUrl = editor.value.getAttributes('link').href
  const url = window.prompt('URL:', previousUrl)

  if (url === null) return
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }
  editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}

watch(() => props.modelValue, (value) => {
  if (editor.value && editor.value.getHTML() !== value) {
    editor.value.commands.setContent(value, false)
  }
})
</script>

<style scoped>
.editor-wrapper {
  border: 1px solid #efeff5;
  border-radius: 4px;
  background: #fff;
}
.toolbar {
  padding: 8px;
  background: #fafafc;
  border-bottom: 1px solid #efeff5;
  position: sticky;
  top: 0;
  z-index: 10;
}
.tiptap-content :deep(.tiptap) {
  min-height: 200px;
  max-height: 400px;
  padding: 12px 16px;
  outline: none;
  overflow-y: auto;
}

/* Стилизация элементов внутри редактора */
:deep(.tiptap) p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}

:deep(.tiptap) h4, :deep(.tiptap) h5 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.2;
}

:deep(.tiptap) ul, :deep(.tiptap) ol {
  padding-left: 1.2em;
  margin: 0.5em 0;
}

:deep(.tiptap) blockquote {
  border-left: 4px solid #F25C03;
  padding-left: 1em;
  color: #666;
  margin: 1em 0;
}

:deep(.tiptap) a {
  color: #F25C03;
  text-decoration: underline;
}
</style>
