#ifndef MAHADIST
#define MAHADIST

#include "Estimate.h"

#include <Eigen/Dense>
using Eigen::MatrixXd;
using Eigen::VectorXd;

void MahaDist(InputParam &input, const MatrixXd &remainCarrier, const MatrixXd &remainJacobian,
	const VectorXd &theta, VectorXd &MahaDistance);

#endif