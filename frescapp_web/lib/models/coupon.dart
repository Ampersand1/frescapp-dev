enum CouponType { percent, fixed }

class Coupon {
  final String code;
  final CouponType type;
  final double amount; // if percent -> 0-100, if fixed -> currency
  final DateTime? expiresAt;
  final double? minCartAmount;
  final int? usageLimitPerUser;

  Coupon({
    required this.code,
    required this.type,
    required this.amount,
    this.expiresAt,
    this.minCartAmount,
    this.usageLimitPerUser,
  });

  bool get isExpired => expiresAt != null && DateTime.now().isAfter(expiresAt!);

  double apply(double cartTotal) {
    // retorna el valor de descuento (no el total final)
    if (isExpired) return 0.0;
    if (minCartAmount != null && cartTotal < minCartAmount!) return 0.0;

    if (type == CouponType.percent) {
      // descuento = cartTotal * (amount / 100)
      return cartTotal * (amount / 100.0);
    } else {
      // fixed amount
      return amount <= cartTotal ? amount : cartTotal;
    }
  }

  Map<String, dynamic> toJson() => {
        'code': code,
        'type': type == CouponType.percent ? 'percent' : 'fixed',
        'amount': amount,
        'expiresAt': expiresAt?.toIso8601String(),
        'minCartAmount': minCartAmount,
        'usageLimitPerUser': usageLimitPerUser,
      };

  static Coupon fromJson(Map<String, dynamic> json) {
    return Coupon(
      code: json['code'] as String,
      type: (json['type'] as String) == 'percent' ? CouponType.percent : CouponType.fixed,
      amount: (json['amount'] as num).toDouble(),
      expiresAt: json['expiresAt'] != null ? DateTime.parse(json['expiresAt']) : null,
      minCartAmount: json['minCartAmount'] != null ? (json['minCartAmount'] as num).toDouble() : null,
      usageLimitPerUser: json['usageLimitPerUser'] != null ? (json['usageLimitPerUser'] as num).toInt() : null,
    );
  }
}
