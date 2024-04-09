import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  srcDir: 'src',
  lastUpdated: true,
  base: "/documentation/",
  title: "Lires document",
  titleTemplate: "Lires",
  description: "Lires documentations",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Manual', link: '/manual/' },
      { text: 'Deployment', link: '/deployment/' },
    ],

    sidebar: [
      {
        text: '用户手册',
        link: '/manual/',
        items: [
          { text: '界面元素', link: '/manual/user-interface' },
          { text: '编辑条目', link: '/manual/add-edit-entry' },
          { text: '添加文档', link: '/manual/add-document' },
          { text: '查找条目', link: '/manual/filter-entry' },
          { text: '阅读文档', link: '/manual/read' },
          { text: 'API', link: '/manual/api' },
        ]
      },
      {
        text: 'Deployment',
        link: '/deployment/',
        items: [
          { text: 'Getting Started', link: '/deployment/gettingStarted' },
          { text: 'Enviroment Variables', link: '/deployment/enviromentVariables' },
          { text: 'Manage', link: '/deployment/manage' },
          { text: 'Dev Guide', link: '/deployment/devGuide' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/menxli/lires' }
    ]
  }
})
