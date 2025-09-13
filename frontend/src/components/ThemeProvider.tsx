import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface ColorScheme {
  name: string
  displayName: string
  shortName: string
  description: string
  colors: {
    primary: string
    secondary: string
    accent: string
    background: string
    surface: string
    text: string
    textSecondary: string
    border: string
    gradientFrom: string
    gradientVia: string
    gradientTo: string
  }
}

const colorSchemes: ColorScheme[] = [
  {
    name: 'warm-amber',
    displayName: '溫暖琥珀',
    shortName: '琥珀',
    description: '溫和的琥珀暖色調',
    colors: {
      primary: '#f59e0b',      // amber-500
      secondary: '#fbbf24',    // amber-400
      accent: '#d97706',       // amber-600
      background: '#fffbeb',   // amber-50
      surface: '#fef3c7',      // amber-100
      text: '#92400e',         // amber-800
      textSecondary: '#b45309', // amber-700
      border: '#fcd34d',       // amber-300
      gradientFrom: '#fef3c7', // amber-100
      gradientVia: '#fde68a',  // amber-200
      gradientTo: '#fcd34d'    // amber-300
    }
  },
  {
    name: 'soft-rose',
    displayName: '柔和玫瑰',
    shortName: '玫瑰',
    description: '溫柔的玫瑰粉色調',
    colors: {
      primary: '#f43f5e',      // rose-500
      secondary: '#fb7185',    // rose-400
      accent: '#e11d48',       // rose-600
      background: '#fff1f2',   // rose-50
      surface: '#fecdd3',      // rose-200
      text: '#9f1239',         // rose-800
      textSecondary: '#be185d', // rose-700
      border: '#fda4af',       // rose-300
      gradientFrom: '#fff1f2', // rose-50
      gradientVia: '#fecdd3',  // rose-200
      gradientTo: '#fda4af'    // rose-300
    }
  },
  {
    name: 'gentle-emerald',
    displayName: '溫和翠綠',
    shortName: '翠綠',
    description: '自然的翠綠色調',
    colors: {
      primary: '#10b981',      // emerald-500
      secondary: '#34d399',    // emerald-400
      accent: '#059669',       // emerald-600
      background: '#ecfdf5',   // emerald-50
      surface: '#d1fae5',      // emerald-100
      text: '#064e3b',         // emerald-800
      textSecondary: '#065f46', // emerald-700
      border: '#a7f3d0',       // emerald-200
      gradientFrom: '#ecfdf5', // emerald-50
      gradientVia: '#d1fae5',  // emerald-100
      gradientTo: '#a7f3d0'    // emerald-200
    }
  },
  {
    name: 'calm-blue',
    displayName: '寧靜海藍',
    shortName: '海藍',
    description: '平靜的海藍色調',
    colors: {
      primary: '#3b82f6',      // blue-500
      secondary: '#60a5fa',    // blue-400
      accent: '#2563eb',       // blue-600
      background: '#eff6ff',   // blue-50
      surface: '#dbeafe',      // blue-100
      text: '#1e3a8a',         // blue-800
      textSecondary: '#1d4ed8', // blue-700
      border: '#93c5fd',       // blue-300
      gradientFrom: '#eff6ff', // blue-50
      gradientVia: '#dbeafe',  // blue-100
      gradientTo: '#bfdbfe'    // blue-200
    }
  },
  {
    name: 'warm-orange',
    displayName: '溫暖橙色',
    shortName: '橙色',
    description: '活力的橙色調',
    colors: {
      primary: '#ea580c',      // orange-600
      secondary: '#fb923c',    // orange-400
      accent: '#c2410c',       // orange-700
      background: '#fff7ed',   // orange-50
      surface: '#fed7aa',      // orange-200
      text: '#9a3412',         // orange-800
      textSecondary: '#c2410c', // orange-700
      border: '#fdba74',       // orange-300
      gradientFrom: '#fff7ed', // orange-50
      gradientVia: '#ffedd5',  // orange-100
      gradientTo: '#fed7aa'    // orange-200
    }
  },
  {
    name: 'gentle-purple',
    displayName: '優雅紫色',
    shortName: '紫色',
    description: '優雅的紫色調',
    colors: {
      primary: '#8b5cf6',      // violet-500
      secondary: '#a78bfa',    // violet-400
      accent: '#7c3aed',       // violet-600
      background: '#f5f3ff',   // violet-50
      surface: '#e0e7ff',      // violet-100
      text: '#5b21b6',         // violet-800
      textSecondary: '#6d28d9', // violet-700
      border: '#c4b5fd',       // violet-300
      gradientFrom: '#f5f3ff', // violet-50
      gradientVia: '#ede9fe',  // violet-100
      gradientTo: '#ddd6fe'    // violet-200
    }
  },
  {
    name: 'mint-fresh',
    displayName: '清新薄荷',
    shortName: '薄荷',
    description: '清新的薄荷綠色調',
    colors: {
      primary: '#06b6d4',      // cyan-500
      secondary: '#22d3ee',    // cyan-400
      accent: '#0891b2',       // cyan-600
      background: '#ecfeff',   // cyan-50
      surface: '#cffafe',      // cyan-100
      text: '#164e63',         // cyan-800
      textSecondary: '#155e75', // cyan-700
      border: '#67e8f9',       // cyan-300
      gradientFrom: '#ecfeff', // cyan-50
      gradientVia: '#cffafe',  // cyan-100
      gradientTo: '#a5f3fc'    // cyan-200
    }
  },
  {
    name: 'warm-coral',
    displayName: '溫暖珊瑚',
    shortName: '珊瑚',
    description: '溫暖的珊瑚色調',
    colors: {
      primary: '#f97316',      // orange-500
      secondary: '#fb923c',    // orange-400
      accent: '#ea580c',       // orange-600
      background: '#fff7ed',   // orange-50
      surface: '#fed7aa',      // orange-200
      text: '#9a3412',         // orange-800
      textSecondary: '#c2410c', // orange-700
      border: '#fdba74',       // orange-300
      gradientFrom: '#fff7ed', // orange-50
      gradientVia: '#ffedd5',  // orange-100
      gradientTo: '#fed7aa'    // orange-200
    }
  },
  {
    name: 'lavender-soft',
    displayName: '柔雅薰衣草',
    shortName: '薰衣草',
    description: '柔雅的薰衣草色調',
    colors: {
      primary: '#a855f7',      // purple-500
      secondary: '#c084fc',    // purple-400
      accent: '#9333ea',       // purple-600
      background: '#faf5ff',   // purple-50
      surface: '#e9d5ff',      // purple-200
      text: '#581c87',         // purple-800
      textSecondary: '#7c3aed', // purple-700
      border: '#c4b5fd',       // purple-300
      gradientFrom: '#faf5ff', // purple-50
      gradientVia: '#f3e8ff',  // purple-100
      gradientTo: '#e9d5ff'    // purple-200
    }
  },
  {
    name: 'forest-green',
    displayName: '森林綠意',
    shortName: '森林',
    description: '深沉的森林綠色調',
    colors: {
      primary: '#059669',      // emerald-600
      secondary: '#10b981',    // emerald-500
      accent: '#047857',       // emerald-700
      background: '#f0fdf4',   // green-50
      surface: '#dcfce7',      // green-100
      text: '#14532d',         // green-800
      textSecondary: '#166534', // green-700
      border: '#86efac',       // green-300
      gradientFrom: '#f0fdf4', // green-50
      gradientVia: '#dcfce7',  // green-100
      gradientTo: '#bbf7d0'    // green-200
    }
  },
  {
    name: 'sunset-gold',
    displayName: '夕陽金輝',
    shortName: '金輝',
    description: '溫暖的金色夕陽色調',
    colors: {
      primary: '#eab308',      // yellow-500
      secondary: '#facc15',    // yellow-400
      accent: '#ca8a04',       // yellow-600
      background: '#fefce8',   // yellow-50
      surface: '#fef3c7',      // yellow-100
      text: '#713f12',         // yellow-800
      textSecondary: '#a16207', // yellow-700
      border: '#fde047',       // yellow-300
      gradientFrom: '#fefce8', // yellow-50
      gradientVia: '#fef9e3',  // yellow-100
      gradientTo: '#fef3c7'    // yellow-200
    }
  }
]

interface ThemeContextType {
  currentScheme: ColorScheme
  setColorScheme: (schemeName: string) => void
  colorSchemes: ColorScheme[]
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [currentScheme, setCurrentScheme] = useState<ColorScheme>(colorSchemes[0])

  const setColorScheme = (schemeName: string) => {
    const scheme = colorSchemes.find(s => s.name === schemeName)
    if (scheme) {
      setCurrentScheme(scheme)
    }
  }

  // Apply colors to CSS custom properties
  useEffect(() => {
    const root = document.documentElement
    const { colors } = currentScheme

    root.style.setProperty('--theme-primary', colors.primary)
    root.style.setProperty('--theme-secondary', colors.secondary)
    root.style.setProperty('--theme-accent', colors.accent)
    root.style.setProperty('--theme-background', colors.background)
    root.style.setProperty('--theme-surface', colors.surface)
    root.style.setProperty('--theme-text', colors.text)
    root.style.setProperty('--theme-text-secondary', colors.textSecondary)
    root.style.setProperty('--theme-border', colors.border)
    root.style.setProperty('--theme-gradient-from', colors.gradientFrom)
    root.style.setProperty('--theme-gradient-via', colors.gradientVia)
    root.style.setProperty('--theme-gradient-to', colors.gradientTo)
  }, [currentScheme])

  return (
    <ThemeContext.Provider value={{ currentScheme, setColorScheme, colorSchemes }}>
      {children}
    </ThemeContext.Provider>
  )
}