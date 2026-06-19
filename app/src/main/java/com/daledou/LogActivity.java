package com.daledou;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LogActivity extends AppCompatActivity {

    private TextView tvLog;
    private ScrollView scrollView;
    private Spinner spinnerLogQQ;
    private String currentQQ = "system";
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_log);

        tvLog = findViewById(R.id.tvLog);
        scrollView = findViewById(R.id.scrollView);
        spinnerLogQQ = findViewById(R.id.spinnerLogQQ);
        Button btnBack = findViewById(R.id.btnBack);
        Button btnRefresh = findViewById(R.id.btnRefresh);
        Button btnClear = findViewById(R.id.btnClear);

        btnBack.setOnClickListener(v -> finish());
        btnRefresh.setOnClickListener(v -> loadLog());
        btnClear.setOnClickListener(v -> clearLog());

        initSpinner();
    }

    private void initSpinner() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String qqStr = bridge.callAttr("get_qq_list").toString();
                List<String> list = new ArrayList<>();
                list.add("system");
                if (!qqStr.isEmpty()) {
                    list.addAll(Arrays.asList(qqStr.split(",")));
                }

                handler.post(() -> {
                    ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                            android.R.layout.simple_spinner_item, list);
                    adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
                    spinnerLogQQ.setAdapter(adapter);
                    spinnerLogQQ.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
                        @Override
                        public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                            currentQQ = list.get(position);
                            loadLog();
                        }
                        @Override
                        public void onNothingSelected(AdapterView<?> parent) {}
                    });
                });
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }

    private void loadLog() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String log = bridge.callAttr("read_log", currentQQ).toString();
                handler.post(() -> {
                    tvLog.setText(log);
                    scrollView.post(() -> scrollView.fullScroll(ScrollView.FOCUS_DOWN));
                });
            } catch (Exception e) {
                handler.post(() -> tvLog.setText("加载日志失败: " + e.getMessage()));
            }
        });
    }

    private void clearLog() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("clear_log", currentQQ);
                handler.post(() -> tvLog.setText("日志已清空"));
            } catch (Exception e) {
                handler.post(() -> tvLog.setText("清空失败: " + e.getMessage()));
            }
        });
    }
}
