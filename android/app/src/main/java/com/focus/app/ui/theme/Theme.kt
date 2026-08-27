package com.focus.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val Sky = Color(0xFF0EA5E9)
private val Violet = Color(0xFF8B5CF6)

private val DarkColors = darkColorScheme(
    primary = Sky,
    secondary = Violet,
    background = Color(0xFF0B1120),
    surface = Color(0xFF111C33),
)

private val LightColors = lightColorScheme(
    primary = Sky,
    secondary = Violet,
)

@Composable
fun FocusTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        content = content,
    )
}
