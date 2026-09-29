/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SkeletonDetail from './SkeletonDetail.vue'

describe('SkeletonDetail', () => {
  it('renders two-column placeholder layout', () => {
    const wrapper = mount(SkeletonDetail)
    expect(wrapper.find('.col-lg-8').exists()).toBe(true)
    expect(wrapper.find('.col-lg-4').exists()).toBe(true)
    expect(wrapper.findAll('.card').length).toBeGreaterThanOrEqual(4)
  })
})
