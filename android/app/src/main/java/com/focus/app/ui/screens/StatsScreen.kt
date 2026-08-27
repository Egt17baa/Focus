package com.focus.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.focus.app.data.EarnedAchievement
import com.focus.app.data.StatsResponse

@Composable
fun StatsScreen(stats: StatsResponse?, achievements: List<EarnedAchievement>) {
    if (stats == null) {
        Box(modifier = Modifier.fillMaxWidth().padding(24.dp)) { Text("Sin datos todavía") }
        return
    }
    val overview = stats.overview
    val maxMinutes = (stats.daily.maxOfOrNull { it.minutes } ?: 0).coerceAtLeast(1)

    LazyColumn(
        modifier = Modifier.fillMaxWidth().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Metric("Minutos", overview.totalMinutes.toString(), Modifier.weight(1f))
                Metric("Sesiones", overview.totalSessions.toString(), Modifier.weight(1f))
                Metric("Racha", "${overview.longestStreak} d", Modifier.weight(1f))
            }
        }
        item {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Últimos 30 días", style = MaterialTheme.typography.titleMedium)
                    Row(
                        modifier = Modifier.fillMaxWidth().height(120.dp),
                        verticalAlignment = Alignment.Bottom,
                        horizontalArrangement = Arrangement.spacedBy(2.dp),
                    ) {
                        stats.daily.takeLast(30).forEach { point ->
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .fillMaxHeight(point.minutes / maxMinutes.toFloat())
                                    .clip(RoundedCornerShape(2.dp))
                                    .background(MaterialTheme.colorScheme.primary),
                            )
                        }
                    }
                    Text(
                        "Tasa de finalización: ${(overview.completionRate * 100).toInt()}%",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }
        }
        if (stats.tags.isNotEmpty()) {
            item {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text("Por etiqueta", style = MaterialTheme.typography.titleMedium)
                        stats.tags.forEach { tag ->
                            Text("${tag.tag}: ${tag.minutes} min · ${tag.sessions} sesiones")
                        }
                    }
                }
            }
        }
        item { Text("Logros", style = MaterialTheme.typography.titleMedium) }
        items(achievements) { earned ->
            Card(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(earned.achievement.icon, style = MaterialTheme.typography.headlineSmall)
                    Column {
                        Text(earned.achievement.name, style = MaterialTheme.typography.titleSmall)
                        Text(earned.achievement.description, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}

@Composable
private fun Metric(label: String, value: String, modifier: Modifier = Modifier) {
    Card(modifier = modifier) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(value, style = MaterialTheme.typography.titleLarge)
            Text(label, style = MaterialTheme.typography.bodySmall)
        }
    }
}
