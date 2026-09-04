use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandChild;
use std::sync::Mutex;

struct BackendProcess(Mutex<Option<CommandChild>>);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())

        .setup(|app| {
            let window = app
                .get_webview_window("main")
                .expect("main window not found");

            let _ = window.set_theme(Some(tauri::Theme::Dark));
            window_vibrancy::apply_mica(&window, None)
                .expect("Unsupported platform or failed to apply Mica");

            let sidecar = app
                .shell()
                .sidecar("backend.exe")
                .expect("failed to create sidecar command");

            let (_rx, child) = sidecar
                .spawn()
                .expect("failed to start backend");

            app.manage(BackendProcess(Mutex::new(Some(child))));

            Ok(())
        })

        .build(tauri::generate_context!())
        .expect("error while building Tauri application")

        .run(|app_handle, event| {
            match event {
                tauri::RunEvent::ExitRequested { .. }
                | tauri::RunEvent::Exit => {
                    if let Some(state) =
                        app_handle.try_state::<BackendProcess>()
                    {
                        if let Ok(mut process) = state.0.lock() {
                            if let Some(child) = process.take() {

                                let pid = child.pid();

                                let _ = std::process::Command::new("taskkill")
                                    .args([
                                        "/PID",
                                        &pid.to_string(),
                                        "/T",
                                        "/F",
                                    ])

                                    .status();
                            }
                        }
                    }
                }

                _ => {}
            }
        });
}
