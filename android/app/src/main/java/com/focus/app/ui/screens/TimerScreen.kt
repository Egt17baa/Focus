package com.focus.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import com.focus.app.data.FocusSession
import com.focus.app.data.Overview
import com.focus.app.data.formatClock
import com.focus.app.data.sessionProgress

private data class Preset(val label: String, val minutes: Int, val mode: String)

private val PRESETS = listOf(
    Preset("Pomodoro", 25, "pomodoro"),
    Preset("Foco largo", 50, "deep_work"),
    Preset("Inmersión", 90, "deep_work"),
    Preset("Descanso", 5, "break"),
)

@Composable
fun TimerScreen(
    session: FocusSession?,
    elapsedSeconds: Int,
    overview: Overview?,
    onStart: (String, Int, String?) -> Unit,
    onPause: () -> Unit,
    onResume: () -> Unit,
    onComplete: () -> Unit,
    onAbandon: () -> Unit,
) {
    var presetIndex by remember { mutableIntStateOf(0) }
    var tag by remember { mutableStateOf("") }
    val preset = PRESETS[presetIndex]
    val plannedSeconds = session?.plannedSeconds ?: preset.minutes * 60
    val remaining = (plannedSeconds - elapsedSeconds).coerceAtLeast(0)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(contentAlignment = Alignment.Center) {
            val progress = sessionProgress(elapsedSeconds, plannedSeconds)
            val ringColor = MaterialTheme.colorScheme.primary
            val trackColor = MaterialTheme.colorScheme.surfaceVariant
            Canvas(modifier = Modifier.size(240.dp)) {
                val stroke = Stroke(width = 22f, cap = StrokeCap.Round)
                val inset = stroke.width
                val arcSize = Size(size.width - inset, size.height - inset)
                drawArc(
                    color = trackColor,
                    startAngle = -90f,
                    sweepAngle = 360f,
                    useCenter = false,
                    style = stroke,
                    size = arcSize,
                    topLeft = androidx.compose.ui.geometry.Offset(inset / 2, inset / 2),
                )
                drawArc(
                    color = ringColor,
                    startAngle = -90f,
                    sweepAngle = 360f * progress,
                    useCenter = false,
                    style = stroke,
                    size = arcSize,
                    topLeft = androidx.compose.ui.geometry.Offset(inset / 2, inset / 2),
                )
            }
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(formatClock(remaining), style = MaterialTheme.typography.displayMedium)
                Text(
                    session?.tag ?: preset.label,
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }

        if (session == null) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                PRESETS.forEachIndexed { index, item ->
                    FilterChip(
                        selected = index == presetIndex,
                        onClick = { presetIndex = index },
                        label = { Text("${item.minutes}m") },
                    )
                }
            }
            OutlinedTextField(
                value = tag,
                onValueChange = { tag = it },
                label = { Text("Etiqueta (estudio, trabajo…)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            Button(
                onClick = { onStart(preset.mode, preset.minutes, tag.ifBlank { null }) },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Empezar ${preset.label}")
            }
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                if (session.isRunning) {
                    OutlinedButton(onClick = onPause) { Text("Pausar") }
                } else {
                    OutlinedButton(onClick = onResume) { Text("Reanudar") }
                }
                Button(onClick = onComplete) { Text("Completar") }
                OutlinedButton(onClick = onAbandon) { Text("Abandonar") }
            }
            Text(
                "Interrupciones: ${session.interruptions}",
                style = MaterialTheme.typography.bodySmall,
            )
        }

        overview?.let { stats ->
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text("Meta diaria", style = MaterialTheme.typography.titleMedium)
                    LinearProgressIndicator(
                        progress = { stats.dailyGoalProgress.toFloat() },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Text("${stats.todayMinutes} / ${stats.dailyGoalMinutes} min hoy")
                    Text("Racha actual: ${stats.currentStreak} días · ${stats.totalPoints} pts")
                }
            }
        }
    }
}
