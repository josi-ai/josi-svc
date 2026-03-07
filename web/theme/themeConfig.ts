import { theme, type ThemeConfig } from 'antd';

const themeConfig: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#6B5CE7',
    colorBgBase: '#0f0a1e',
    colorBgContainer: '#1a1230',
    colorBgElevated: '#231845',
    colorBgLayout: '#0f0a1e',
    borderRadius: 8,
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    colorLink: '#6B5CE7',
    colorSuccess: '#52c41a',
    colorWarning: '#E78A5C',
    colorError: '#ff4d4f',
  },
  components: {
    Layout: {
      siderBg: '#0f0a1e',
      headerBg: '#1a1230',
      bodyBg: '#0f0a1e',
      triggerBg: '#231845',
    },
    Menu: {
      darkItemBg: '#0f0a1e',
      darkItemSelectedBg: '#231845',
      darkItemHoverBg: '#1a1230',
      darkItemSelectedColor: '#6B5CE7',
    },
    Card: {
      colorBgContainer: '#231845',
      colorBorderSecondary: '#2d2060',
    },
    Button: {
      colorPrimary: '#6B5CE7',
      colorPrimaryHover: '#7d70ef',
      primaryShadow: '0 2px 8px rgba(107, 92, 231, 0.3)',
    },
    Input: {
      colorBgContainer: '#1a1230',
      colorBorder: '#2d2060',
      activeBorderColor: '#6B5CE7',
      hoverBorderColor: '#6B5CE7',
    },
  },
};

export default themeConfig;
