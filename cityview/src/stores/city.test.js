import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

let useCityStore

describe('city store fallback and health resolution', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    global.window = {}
    const module = await import('./city.js')
    useCityStore = module.useCityStore
  })

  it('applies demo fallback when no live signals are available', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false })
    const city = useCityStore()

    await city.poll()

    expect(city.buildings.every((building) => building.health !== 'unknown')).toBe(true)
    expect(city.cityHealth).toBeGreaterThan(0)
    expect(city.skyMood).toBe('healthy')
  })

  it('reads health from either job keys or building-id keys', () => {
    const city = useCityStore()

    city.spiritStatus = { buildings: { prometheus: 'down' } }
    const libraryFromJob = city.buildings.find((building) => building.id === 'library')
    expect(libraryFromJob.health).toBe('down')

    city.spiritStatus = { buildings: { library: 'up' } }
    const libraryFromId = city.buildings.find((building) => building.id === 'library')
    expect(libraryFromId.health).toBe('up')
  })
})
