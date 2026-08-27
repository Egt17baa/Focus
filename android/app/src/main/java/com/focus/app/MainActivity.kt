package com.focus.app

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Block
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.focus.app.ui.FocusViewModel
import com.focus.app.ui.screens.AppsScreen
import com.focus.app.ui.screens.AuthScreen
import com.focus.app.ui.screens.StatsScreen
import com.focus.app.ui.screens.TimerScreen
import com.focus.app.ui.theme.FocusTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            FocusTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    FocusApp()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FocusApp(viewModel: FocusViewModel = viewModel(factory = FocusViewModel.Factory)) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val snackbar = remember { SnackbarHostState() }
    var tab by remember { mutableIntStateOf(0) }

    val notificationPermission = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { }

    LaunchedEffect(state.isAuthenticated) {
        if (state.isAuthenticated && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    LaunchedEffect(state.error) {
        state.error?.let {
            snackbar.showSnackbar(it)
            viewModel.dismissError()
        }
    }

    LaunchedEffect(state.justUnlocked) {
        state.justUnlocked.forEach { snackbar.showSnackbar("${it.achievement.icon} ${it.achievement.name}") }
        if (state.justUnlocked.isNotEmpty()) viewModel.dismissUnlocked()
    }

    if (!state.isAuthenticated) {
        Box(modifier = Modifier.fillMaxSize()) {
            AuthScreen(
                loading = state.loading,
                error = state.error,
                onLogin = { identifier, password -> viewModel.login(identifier, password) },
                onRegister = { username, email, password ->
                    viewModel.register(username, email, password)
                },
            )
            if (state.loading) {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.TopCenter))
            }
        }
        return
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbar) },
        topBar = {
            TopAppBar(
                title = {
                    Text("${state.user?.avatarEmoji ?: ""} ${state.user?.username ?: "Focus"}")
                },
                actions = {
                    Text("${state.user?.totalFocusPoints ?: 0} pts")
                    IconButton(onClick = viewModel::logout) {
                        Icon(Icons.AutoMirrored.Filled.Logout, contentDescription = "Cerrar sesión")
                    }
                },
            )
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = tab == 0,
                    onClick = { tab = 0 },
                    icon = { Icon(Icons.Default.Timer, contentDescription = null) },
                    label = { Text("Foco") },
                )
                NavigationBarItem(
                    selected = tab == 1,
                    onClick = {
                        tab = 1
                        viewModel.refresh()
                    },
                    icon = { Icon(Icons.Default.BarChart, contentDescription = null) },
                    label = { Text("Progreso") },
                )
                NavigationBarItem(
                    selected = tab == 2,
                    onClick = { tab = 2 },
                    icon = { Icon(Icons.Default.Block, contentDescription = null) },
                    label = { Text("Apps") },
                )
            }
        },
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding)) {
            when (tab) {
                0 -> TimerScreen(
                    session = state.session,
                    elapsedSeconds = state.elapsedSeconds,
                    overview = state.stats?.overview,
                    onStart = { mode, minutes, tag -> viewModel.start(mode, minutes, tag) },
                    onPause = { viewModel.pause() },
                    onResume = { viewModel.resume() },
                    onComplete = { viewModel.complete() },
                    onAbandon = { viewModel.abandon() },
                )
                1 -> StatsScreen(stats = state.stats, achievements = state.achievements)
                else -> AppsScreen(
                    apps = state.blockedApps,
                    onAdd = { name, packageName -> viewModel.addBlockedApp(name, packageName) },
                    onRemove = { id -> viewModel.removeBlockedApp(id) },
                )
            }
        }
    }
}
