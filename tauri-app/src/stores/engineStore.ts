import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface EngineState {
  geoMode: 'select' | 'manual'
  continent: string
  country: string
  city: string
  district: string
  manualAddress: string
  category: string
  kwText: string
  concurrency: number
  aiSeed: string
  aiNum: number

  setGeoMode: (mode: 'select' | 'manual') => void
  setContinent: (v: string) => void
  setCountry: (v: string) => void
  setCity: (v: string) => void
  setDistrict: (v: string) => void
  setManualAddress: (v: string) => void
  setCategory: (v: string) => void
  setKwText: (v: string | ((prev: string) => string)) => void
  setConcurrency: (v: number) => void
  setAiSeed: (v: string) => void
  setAiNum: (v: number) => void
}

export const useEngineStore = create<EngineState>()(
  persist(
    (set) => ({
      geoMode: 'select',
      continent: '',
      country: '',
      city: '',
      district: '所有',
      manualAddress: '',
      category: '',
      kwText: '',
      concurrency: 3,
      aiSeed: '',
      aiNum: 7,

      setGeoMode: (geoMode) => set({ geoMode }),
      setContinent: (continent) => set({ continent }),
      setCountry: (country) => set({ country }),
      setCity: (city) => set({ city }),
      setDistrict: (district) => set({ district }),
      setManualAddress: (manualAddress) => set({ manualAddress }),
      setCategory: (category) => set({ category }),
      setKwText: (kwText) => set((state) => ({ kwText: typeof kwText === 'function' ? kwText(state.kwText) : kwText })),
      setConcurrency: (concurrency) => set({ concurrency }),
      setAiSeed: (aiSeed) => set({ aiSeed }),
      setAiNum: (aiNum) => set({ aiNum }),
    }),
    {
      name: 'b2b-engine-state',
    }
  )
)
