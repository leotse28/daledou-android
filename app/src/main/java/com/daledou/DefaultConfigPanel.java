package com.daledou;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class DefaultConfigPanel {

    private final Context ctx;
    private final EditText etConfig;
    private final TextView tvMsg;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());

    public DefaultConfigPanel(Context ctx, View root) {
        this.ctx = ctx;
        etConfig = root.findViewById(R.id.etDefaultConfig);
        tvMsg    = root.findViewById(R.id.tvDefaultMsg);

        root.findViewById(R.id.btnSaveDefault).setOnClickListener(v -> save());
        root.findViewById(R.id.btnResetDefault).setOnClickListener(v -> reset());
    }

    public void onShow() {
        load();
    }

    private void load() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String content = bridge.callAttr("load_default_config").toString();
                handler.post(() -> {
                    etConfig.setText(content);
                    setMsg("✅ 已加载 default.yaml", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 加载失败: " + e.getMessage(), false));
            }
        });
    }

    private void save() {
        String content = etConfig.getText().toString();
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("save_default_config", content);
                handler.post(() -> setMsg("✅ default.yaml 已保存", true));
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 保存失败: " + e.getMessage(), false));
            }
        });
    }

    private void reset() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("reset_default_config");
                String content = bridge.callAttr("load_default_config").toString();
                handler.post(() -> {
                    etConfig.setText(content);
                    setMsg("✅ 已还原为出厂默认配置", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 还原失败: " + e.getMessage(), false));
            }
        });
    }

    private void setMsg(String msg, boolean ok) {
        tvMsg.setText(msg);
        tvMsg.setTextColor(ok ? 0xFF2ECC71 : 0xFFE74C3C);
    }
}
