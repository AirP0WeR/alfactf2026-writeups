package io.peakmood.mobile;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffColorFilter;
import android.graphics.Rect;
import android.graphics.RectF;
import android.os.SystemClock;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/* JADX INFO: loaded from: classes.dex */
public class MiningSceneView extends View {
    private static final long FLASH_DURATION_MS = 220;
    private static final long SWING_DURATION_MS = 620;
    private final Paint bitmapPaint;
    private final Paint bitmapShadowPaint;
    private final Paint bitmapUnderlayPaint;
    private final Paint coreFillPaint;
    private final Paint corePlatePaint;
    private final Paint crackPaint;
    private float damageProgress;
    private long flashStartedAtMs;
    private final Bitmap[] geodeFrames;
    private final Paint geodePlatePaint;
    private final RectF geodeRect;
    private final RectF geodeShadowRect;
    private final Paint glowPaint;
    private Bitmap hammerBitmap;
    private final Matrix hammerMatrix;
    private final Matrix hammerShadowMatrix;
    private boolean nodeActive;
    private OnNodeTapListener nodeTapListener;
    private final Paint ringPaint;
    private final Paint shadowPaint;
    private final RectF shadowRect;
    private final Paint shardPaint;
    private final List<Shard> shards;
    private long swingStartedAtMs;
    private String tier;

    public interface OnNodeTapListener {
        void onNodeTap();
    }

    public MiningSceneView(Context context) {
        this(context, null);
    }

    public MiningSceneView(Context context, AttributeSet attributeSet) {
        super(context, attributeSet);
        this.geodeFrames = new Bitmap[12];
        this.bitmapPaint = new Paint(3);
        this.bitmapShadowPaint = new Paint(3);
        this.bitmapUnderlayPaint = new Paint(3);
        this.glowPaint = new Paint(1);
        this.geodePlatePaint = new Paint(1);
        this.coreFillPaint = new Paint(1);
        this.corePlatePaint = new Paint(1);
        this.ringPaint = new Paint(1);
        this.crackPaint = new Paint(1);
        this.shardPaint = new Paint(1);
        this.shadowPaint = new Paint(1);
        this.hammerMatrix = new Matrix();
        this.hammerShadowMatrix = new Matrix();
        this.geodeRect = new RectF();
        this.shadowRect = new RectF();
        this.geodeShadowRect = new RectF();
        this.shards = new ArrayList();
        this.nodeActive = false;
        this.tier = "none";
        this.damageProgress = 0.0f;
        this.swingStartedAtMs = -1L;
        this.flashStartedAtMs = -1L;
        loadBitmaps();
        this.bitmapShadowPaint.setColorFilter(new PorterDuffColorFilter(Color.argb(190, 6, 12, 16), PorterDuff.Mode.SRC_IN));
        this.bitmapUnderlayPaint.setColorFilter(new PorterDuffColorFilter(Color.argb(255, 232, 239, 242), PorterDuff.Mode.SRC_ATOP));
        this.glowPaint.setStyle(Paint.Style.FILL);
        this.geodePlatePaint.setStyle(Paint.Style.FILL);
        this.geodePlatePaint.setColor(Color.argb(216, 4, 8, 10));
        this.corePlatePaint.setStyle(Paint.Style.FILL);
        this.corePlatePaint.setColor(Color.argb(250, 6, 10, 12));
        this.coreFillPaint.setStyle(Paint.Style.FILL);
        this.coreFillPaint.setColor(Color.argb(255, 13, 18, 22));
        this.ringPaint.setStyle(Paint.Style.STROKE);
        this.ringPaint.setStrokeWidth(dp(2.2f));
        this.crackPaint.setStyle(Paint.Style.STROKE);
        this.crackPaint.setStrokeCap(Paint.Cap.ROUND);
        this.crackPaint.setStrokeJoin(Paint.Join.ROUND);
        this.shadowPaint.setStyle(Paint.Style.FILL);
        this.shadowPaint.setColor(Color.argb(118, 7, 9, 12));
        setClickable(true);
    }

    private void loadBitmaps() {
        int i = 0;
        while (i < this.geodeFrames.length) {
            this.geodeFrames[i] = boostBitmapAlpha(BitmapFactory.decodeResource(getResources(), getResources().getIdentifier("ar_geode_" + (i < 10 ? "0" + i : String.valueOf(i)), "drawable", getContext().getPackageName())), 2.4f, 108);
            i++;
        }
        this.hammerBitmap = boostBitmapAlpha(BitmapFactory.decodeResource(getResources(), R.drawable.ar_hammer), 3.1f, 126);
    }

    private Bitmap boostBitmapAlpha(Bitmap bitmap, float f, int i) {
        if (bitmap == null) {
            return null;
        }
        Bitmap bitmapCopy = bitmap.copy(Bitmap.Config.ARGB_8888, true);
        if (bitmapCopy == null) {
            return bitmap;
        }
        int width = bitmapCopy.getWidth();
        int height = bitmapCopy.getHeight();
        int i2 = width * height;
        int[] iArr = new int[i2];
        bitmapCopy.getPixels(iArr, 0, width, 0, 0, width, height);
        for (int i3 = 0; i3 < i2; i3++) {
            int i4 = iArr[i3];
            int iAlpha = Color.alpha(i4);
            if (iAlpha != 0) {
                iArr[i3] = Color.argb(Math.max(i, Math.min(255, Math.round(iAlpha * f))), Color.red(i4), Color.green(i4), Color.blue(i4));
            }
        }
        bitmapCopy.setPixels(iArr, 0, width, 0, 0, width, height);
        return bitmapCopy;
    }

    public void setOnNodeTapListener(OnNodeTapListener onNodeTapListener) {
        this.nodeTapListener = onNodeTapListener;
    }

    public void clearNode() {
        this.nodeActive = false;
        this.tier = "none";
        this.damageProgress = 0.0f;
        this.swingStartedAtMs = -1L;
        this.flashStartedAtMs = -1L;
        this.shards.clear();
        invalidate();
    }

    public void setNodeState(boolean z, String str, int i, int i2) {
        this.nodeActive = z;
        if (str == null) {
            str = "none";
        }
        this.tier = str;
        if (!z || i2 <= 0) {
            this.damageProgress = 0.0f;
            this.swingStartedAtMs = -1L;
            this.flashStartedAtMs = -1L;
        } else {
            this.damageProgress = 1.0f - (i / i2);
        }
        invalidate();
    }

    public boolean isImpactAnimationRunning() {
        return this.swingStartedAtMs > 0 && SystemClock.uptimeMillis() - this.swingStartedAtMs < SWING_DURATION_MS;
    }

    public boolean triggerImpact() {
        if (!this.nodeActive || isImpactAnimationRunning()) {
            return false;
        }
        long jUptimeMillis = SystemClock.uptimeMillis();
        this.swingStartedAtMs = jUptimeMillis;
        this.flashStartedAtMs = jUptimeMillis;
        spawnShards(jUptimeMillis);
        invalidate();
        return true;
    }

    @Override // android.view.View
    public boolean onTouchEvent(MotionEvent motionEvent) {
        if (!this.nodeActive || this.nodeTapListener == null) {
            return super.onTouchEvent(motionEvent);
        }
        if (motionEvent.getAction() != 1 || !this.geodeRect.contains(motionEvent.getX(), motionEvent.getY()) || isImpactAnimationRunning()) {
            return true;
        }
        this.nodeTapListener.onNodeTap();
        return true;
    }

    @Override // android.view.View
    protected void onDraw(Canvas canvas) {
        long j;
        super.onDraw(canvas);
        long jUptimeMillis = SystemClock.uptimeMillis();
        float width = getWidth();
        float height = getHeight();
        float f = width * 0.5f;
        float f2 = 0.64f * height;
        float fSin = this.nodeActive ? ((float) Math.sin(jUptimeMillis * 0.0022f)) * dp(7.0f) : 0.0f;
        float fSin2 = this.nodeActive ? (((float) Math.sin(jUptimeMillis * 0.0031f)) * 0.02f) + 1.0f : 1.0f;
        if (this.nodeActive) {
            int iTierColor = tierColor(this.tier);
            this.glowPaint.setColor(iTierColor);
            j = 0;
            this.glowPaint.setAlpha(((int) (((Math.sin(jUptimeMillis * 0.0038f) * 0.5d) + 0.5d) * 18.0d)) + 36);
            float f3 = f2 + fSin;
            canvas.drawCircle(f, f3, dp((this.damageProgress * 20.0f) + 142.0f), this.glowPaint);
            canvas.drawCircle(f, f3, dp(122.0f), this.geodePlatePaint);
            canvas.drawCircle(f, f3, dp(106.0f), this.corePlatePaint);
            canvas.drawCircle(f, f3, dp(96.0f), this.coreFillPaint);
            this.ringPaint.setColor(iTierColor);
            this.ringPaint.setAlpha(158);
            canvas.drawCircle(f, f3, dp(116.0f), this.ringPaint);
            this.ringPaint.setAlpha(118);
            canvas.drawCircle(f, f3, dp(134.0f), this.ringPaint);
            this.shadowRect.set(f - dp(118.0f), dp(108.0f) + f2, dp(118.0f) + f, dp(152.0f) + f2);
            canvas.drawOval(this.shadowRect, this.shadowPaint);
            Bitmap bitmap = this.geodeFrames[(int) ((jUptimeMillis / 90) % ((long) this.geodeFrames.length))];
            float fDp = dp(246.0f) * fSin2 * 0.5f;
            this.geodeRect.set(f - fDp, (f2 - fDp) + fSin, f + fDp, fDp + f2 + fSin);
            this.geodeShadowRect.set(this.geodeRect);
            this.geodeShadowRect.offset(dp(3.0f), dp(8.0f));
            if (this.flashStartedAtMs > 0) {
                float fMin = 1.0f - Math.min(1.0f, (jUptimeMillis - this.flashStartedAtMs) / 220.0f);
                this.bitmapShadowPaint.setAlpha(214);
                canvas.drawBitmap(bitmap, (Rect) null, this.geodeShadowRect, this.bitmapShadowPaint);
                this.bitmapUnderlayPaint.setAlpha(214);
                canvas.drawBitmap(bitmap, (Rect) null, this.geodeRect, this.bitmapUnderlayPaint);
                this.bitmapPaint.setAlpha(255);
                canvas.drawBitmap(bitmap, (Rect) null, this.geodeRect, this.bitmapPaint);
                if (fMin <= 0.0f) {
                    this.flashStartedAtMs = -1L;
                } else {
                    this.glowPaint.setColor(-1);
                    this.glowPaint.setAlpha((int) (fMin * 104.0f));
                    canvas.drawCircle(f, f3, dp((fMin * 34.0f) + 104.0f), this.glowPaint);
                }
            } else {
                this.bitmapShadowPaint.setAlpha(214);
                canvas.drawBitmap(bitmap, (Rect) null, this.geodeShadowRect, this.bitmapShadowPaint);
                this.bitmapUnderlayPaint.setAlpha(214);
                canvas.drawBitmap(bitmap, (Rect) null, this.geodeRect, this.bitmapUnderlayPaint);
                this.bitmapPaint.setAlpha(255);
                canvas.drawBitmap(bitmap, (Rect) null, this.geodeRect, this.bitmapPaint);
            }
            drawCracks(canvas, f, f3);
            drawShards(canvas, jUptimeMillis);
        } else {
            j = 0;
            this.geodeRect.setEmpty();
        }
        drawHammer(canvas, jUptimeMillis, width, height, f, f2 + fSin);
        if (this.nodeActive || this.swingStartedAtMs > j || !this.shards.isEmpty()) {
            postInvalidateOnAnimation();
        }
    }

    private void drawCracks(Canvas canvas, float f, float f2) {
        if (this.damageProgress <= 0.05f) {
            return;
        }
        this.crackPaint.setColor(Color.argb(210, 220, 245, 255));
        this.crackPaint.setStrokeWidth(dp((this.damageProgress * 3.0f) + 1.5f));
        float fDp = dp(86.0f);
        int iMax = Math.max(0, (int) Math.floor(this.damageProgress * 5.0f)) + 2;
        for (int i = 0; i < iMax; i++) {
            double d = i;
            Double.isNaN(d);
            double d2 = this.damageProgress * 0.22f;
            Double.isNaN(d2);
            float f3 = (float) ((d * 1.0471975511965976d) + 0.34d + d2);
            Path path = new Path();
            double d3 = f3;
            path.moveTo((((float) Math.cos(d3)) * fDp * 0.12f) + f, (((float) Math.sin(d3)) * fDp * 0.12f) + f2);
            for (int i2 = 1; i2 <= 4; i2++) {
                float f4 = i2 % 2 == 0 ? -0.24f : 0.17f;
                float f5 = ((i2 * 0.16f) + 0.24f + (this.damageProgress * 0.08f)) * fDp;
                double d4 = f4 + f3;
                path.lineTo((((float) Math.cos(d4)) * f5) + f, (((float) Math.sin(d4)) * f5) + f2);
            }
            canvas.drawPath(path, this.crackPaint);
        }
    }

    private void drawHammer(Canvas canvas, long j, float f, float f2, float f3, float f4) {
        float fLerp;
        float fLerp2;
        float fLerp3;
        float fLerp4;
        float f5;
        if (this.hammerBitmap == null) {
            return;
        }
        float fDp = f3 - dp(70.0f);
        float fDp2 = f4 - dp(132.0f);
        float fDp3 = f3 - dp(6.0f);
        float fDp4 = f4 - dp(50.0f);
        if (this.swingStartedAtMs <= 0) {
            fLerp = -24.0f;
            fLerp2 = fDp2;
            fLerp3 = fDp;
            fLerp4 = 0.94f;
        } else {
            float fMin = Math.min(1.0f, (j - this.swingStartedAtMs) / 620.0f);
            if (fMin < 0.58f) {
                f5 = fMin / 0.58f;
            } else {
                f5 = 1.0f - ((fMin - 0.58f) / 0.42f);
            }
            double dMax = Math.max(0.0f, Math.min(1.0f, f5));
            Double.isNaN(dMax);
            float fSin = (float) Math.sin(dMax * 3.141592653589793d * 0.8199999928474426d);
            fLerp3 = lerp(f3 - dp(86.0f), fDp3, fSin);
            fLerp2 = lerp(f4 - dp(146.0f), fDp4, fSin);
            fLerp = lerp(-28.0f, 58.0f, fSin);
            fLerp4 = lerp(0.92f, 1.02f, fSin);
            if (fMin >= 1.0f) {
                this.swingStartedAtMs = -1L;
            }
        }
        this.hammerMatrix.reset();
        this.hammerMatrix.postScale(fLerp4, fLerp4);
        this.hammerMatrix.postTranslate((-(this.hammerBitmap.getWidth() * fLerp4)) * 0.36f, (-(this.hammerBitmap.getHeight() * fLerp4)) * 0.18f);
        this.hammerMatrix.postRotate(fLerp);
        this.hammerMatrix.postTranslate(fLerp3, fLerp2);
        this.hammerShadowMatrix.set(this.hammerMatrix);
        this.hammerShadowMatrix.postTranslate(dp(3.0f), dp(6.0f));
        this.bitmapShadowPaint.setAlpha(206);
        canvas.drawBitmap(this.hammerBitmap, this.hammerShadowMatrix, this.bitmapShadowPaint);
        this.bitmapUnderlayPaint.setAlpha(224);
        canvas.drawBitmap(this.hammerBitmap, this.hammerMatrix, this.bitmapUnderlayPaint);
        canvas.drawBitmap(this.hammerBitmap, this.hammerMatrix, this.bitmapPaint);
    }

    private void spawnShards(long j) {
        this.shards.clear();
        int iTierColor = tierColor(this.tier);
        for (int i = 0; i < 9; i++) {
            double d = i;
            Double.isNaN(d);
            double d2 = 9;
            Double.isNaN(d2);
            this.shards.add(new Shard((float) (((d * 6.283185307179586d) / d2) + 0.18d), dp((i * 0.26f) + 1.8f), j, iTierColor));
        }
    }

    private void drawShards(Canvas canvas, long j) {
        Iterator<Shard> it = this.shards.iterator();
        while (it.hasNext()) {
            Shard next = it.next();
            float f = (j - next.startedAtMs) / 520.0f;
            if (f >= 1.0f) {
                it.remove();
            } else {
                float f2 = 1.0f - f;
                float fDp = next.speed * f * dp(48.0f);
                float fCenterX = this.geodeRect.centerX() + (((float) Math.cos(next.angle)) * fDp);
                float fCenterY = (this.geodeRect.centerY() + (((float) Math.sin(next.angle)) * fDp)) - (f * dp(22.0f));
                this.shardPaint.setColor(next.color);
                this.shardPaint.setAlpha((int) (180.0f * f2));
                canvas.drawCircle(fCenterX, fCenterY, dp((f2 * 2.4f) + 2.0f), this.shardPaint);
            }
        }
    }

    private float dp(float f) {
        return f * getResources().getDisplayMetrics().density;
    }

    private float lerp(float f, float f2, float f3) {
        return f + ((f2 - f) * f3);
    }

    private int tierColor(String str) {
        if ("common".equals(str)) {
            return Color.parseColor("#6BD8C6");
        }
        if ("rare".equals(str)) {
            return Color.parseColor("#7DB0FF");
        }
        if ("epic".equals(str)) {
            return Color.parseColor("#FFB766");
        }
        if ("FLAG".equals(str)) {
            return Color.parseColor("#FF7363");
        }
        return Color.parseColor("#9EF2DE");
    }

    private static final class Shard {
        final float angle;
        final int color;
        final float speed;
        final long startedAtMs;

        Shard(float f, float f2, long j, int i) {
            this.angle = f;
            this.speed = f2;
            this.startedAtMs = j;
            this.color = i;
        }
    }
}
