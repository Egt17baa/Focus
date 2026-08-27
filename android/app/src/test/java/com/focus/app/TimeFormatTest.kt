package com.focus.app

import com.focus.app.data.formatClock
import com.focus.app.data.sessionProgress
import org.junit.Assert.assertEquals
import org.junit.Test

class TimeFormatTest {
    @Test
    fun `formats minutes and seconds`() {
        assertEquals("25:00", formatClock(1500))
        assertEquals("00:09", formatClock(9))
    }

    @Test
    fun `clamps negative values`() {
        assertEquals("00:00", formatClock(-30))
    }

    @Test
    fun `formats sessions longer than one hour`() {
        assertEquals("1:30:05", formatClock(5405))
    }

    @Test
    fun `progress is clamped between zero and one`() {
        assertEquals(0.5f, sessionProgress(750, 1500), 0.001f)
        assertEquals(1f, sessionProgress(3000, 1500), 0.001f)
        assertEquals(0f, sessionProgress(100, 0), 0.001f)
    }
}
