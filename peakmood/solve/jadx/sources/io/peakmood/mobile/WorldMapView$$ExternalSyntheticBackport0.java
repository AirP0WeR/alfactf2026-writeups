package io.peakmood.mobile;

/* JADX INFO: compiled from: D8$$SyntheticClass */
/* JADX INFO: loaded from: classes.dex */
public final /* synthetic */ class WorldMapView$$ExternalSyntheticBackport0 {
    public static /* synthetic */ int m(int i, int i2) {
        int i3 = i % i2;
        if (i3 == 0) {
            return 0;
        }
        return (((i ^ i2) >> 31) | 1) > 0 ? i3 : i3 + i2;
    }
}
